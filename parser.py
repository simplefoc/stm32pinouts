
import os
import re
import urllib.request
import urllib.error


SVD_INDEX_CACHE = None
SVD_CONTENT_CACHE = {}

def sanitize_filename(name):
    # Replace any invalid characters with underscores
    return re.sub(r'[^\w\-_.() ]', '_', name)


def format_display_name(name):
    # Improve readability for navigation labels while preserving raw names elsewhere for search.
    display = re.sub(r"[_\[\]\(\)]", " ", name)
    display = re.sub(r"\s+", " ", display).strip()
    return display


def build_search_aliases(raw_name):
    # Build explicit aliases users can use with browser search (Ctrl+F).
    aliases = []
    readable = format_display_name(raw_name)
    exploded = re.sub(r"[^A-Za-z0-9]+", " ", raw_name)
    exploded = re.sub(r"\s+", " ", exploded).strip()

    for candidate in [raw_name, readable, exploded]:
        if candidate and candidate not in aliases:
            aliases.append(candidate)

    return aliases


def dedupe_preserve_order(items):
    unique_items = []
    for item in items:
        if item and item not in unique_items:
            unique_items.append(item)
    return unique_items


def expand_parentheses_token(token):
    # Expand token options like WLE4J(8-B-C)I -> WLE4J8I, WLE4JBI, WLE4JCI.
    match = re.search(r"\(([^()]+)\)", token)
    if not match:
        return [token]

    options = [opt.strip() for opt in match.group(1).split("-") if opt.strip()]
    expanded = []
    for option in options:
        expanded_token = token[:match.start()] + option + token[match.end():]
        expanded.extend(expand_parentheses_token(expanded_token))

    return dedupe_preserve_order(expanded)


def expand_subfamily_rows(raw_name):
    # Split grouped folder names into individual searchable rows.
    row_candidates = []
    for token in [part for part in raw_name.split("_") if part]:
        row_candidates.extend(expand_parentheses_token(token))
    return dedupe_preserve_order(row_candidates)


def normalize_identifier(value):
    return re.sub(r"[^A-Za-z0-9]", "", value).upper()


def row_matches_variant(row_name, variant_name):
    # Best-effort match: full token first, then relaxed suffix trims.
    row_norm = normalize_identifier(row_name)
    variant_norm = normalize_identifier(variant_name)
    if not row_norm or not variant_norm:
        return False

    if row_norm in variant_norm or variant_norm in row_norm:
        return True

    # Package/suffix chars often differ between row and variant naming.
    for trim in range(1, min(4, len(row_norm) - 5)):
        token = row_norm[:-trim]
        if len(token) >= 6 and token in variant_norm:
            return True

    return False


def filter_variants_for_row(row_name, variant_names):
    return [variant for variant in variant_names if row_matches_variant(row_name, variant)]


def parse_boards_entry_file(subfamily_path):
    boards_entry_path = os.path.join(subfamily_path, "boards_entry.txt")
    if not os.path.isfile(boards_entry_path):
        return []

    entries = {}
    with open(boards_entry_path, "r") as file:
        for raw_line in file:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue

            # Example key:
            # GenWL.menu.pnum.GENERIC_WLE4J8IX.upload.maximum_size=65536
            match = re.match(r".*\.menu\.pnum\.GENERIC_([A-Z0-9_]+)(?:\.(.+))?=(.*)", line)
            if not match:
                continue

            board_id = match.group(1)
            field = match.group(2)
            value = match.group(3).strip()

            if board_id not in entries:
                entries[board_id] = {
                    "board_id": board_id,
                    "label": "",
                    "product_line": "",
                    "flash_bytes": "",
                    "ram_bytes": "",
                    "svd_file": ""
                }

            entry = entries[board_id]
            if field is None:
                entry["label"] = value
            elif field == "build.product_line":
                entry["product_line"] = value
            elif field == "upload.maximum_size":
                entry["flash_bytes"] = value
            elif field == "upload.maximum_data_size":
                entry["ram_bytes"] = value
            elif field == "debug.svd_file":
                entry["svd_file"] = value

    return sorted(entries.values(), key=lambda e: e["board_id"])


def format_size_from_bytes(size_bytes):
    if not size_bytes or not str(size_bytes).isdigit():
        return "-"

    size = int(size_bytes)
    kb = size // 1024
    if kb >= 1024:
        mb = kb / 1024.0
        return f"{mb:.1f} MB"
    return f"{kb} KB"


def filter_board_entries_for_row(row_name, board_entries):
    return [entry for entry in board_entries if row_matches_variant(row_name, entry["board_id"])]


def summarize_board_entries(board_entries):
    if not board_entries:
        return "-"

    product_lines = dedupe_preserve_order([entry["product_line"] for entry in board_entries if entry["product_line"]])
    flashes = dedupe_preserve_order([format_size_from_bytes(entry["flash_bytes"]) for entry in board_entries if entry["flash_bytes"]])
    rams = dedupe_preserve_order([format_size_from_bytes(entry["ram_bytes"]) for entry in board_entries if entry["ram_bytes"]])

    parts = []
    if product_lines:
        parts.append("/".join(product_lines))
    if flashes or rams:
        parts.append(f"Flash: {'/'.join(flashes) if flashes else '-'}")
        parts.append(f"RAM: {'/'.join(rams) if rams else '-'}")

    return "<br>".join(parts) if parts else "-"


def summarize_product_lines(board_entries):
    if not board_entries:
        return "-"
    product_lines = dedupe_preserve_order([entry["product_line"] for entry in board_entries if entry["product_line"]])
    return "<br>".join(product_lines) if product_lines else "-"


def summarize_flash_sizes(board_entries):
    if not board_entries:
        return "-"
    flashes = dedupe_preserve_order([format_size_from_bytes(entry["flash_bytes"]) for entry in board_entries if entry["flash_bytes"]])
    return "<br>".join(flashes) if flashes else "-"


def summarize_ram_sizes(board_entries):
    if not board_entries:
        return "-"
    rams = dedupe_preserve_order([format_size_from_bytes(entry["ram_bytes"]) for entry in board_entries if entry["ram_bytes"]])
    return "<br>".join(rams) if rams else "-"


def infer_package_code(part_name):
    # Best-effort extraction of package code from STM32 part token.
    token = re.sub(r"[^A-Za-z0-9]", "", part_name).upper()
    if not token:
        return "-"
    # Generic board IDs often end with wildcard "X" (for example H745IGTX).
    # Trim that marker first so package extraction remains meaningful.
    token = re.sub(r"X+$", "", token)
    if not token:
        return "-"
    # Most STM32 part tokens end with package/temperature code letters.
    match = re.search(r"([A-Z])$", token)
    return match.group(1) if match else "-"


def format_frequency_hz(hz_value):
    if not hz_value:
        return "-"

    hz = int(hz_value)
    if hz >= 1000000:
        return f"{hz / 1000000:.1f} MHz"
    if hz >= 1000:
        return f"{hz / 1000:.1f} kHz"
    return f"{hz} Hz"


def find_svd_file_in_repo(core_root, svd_file_value):
    global SVD_INDEX_CACHE

    svd_basename = os.path.basename(svd_file_value)
    if not svd_basename:
        return None

    if SVD_INDEX_CACHE is None:
        SVD_INDEX_CACHE = {}
        search_roots = []
        if os.path.isdir(local_svd_root):
            search_roots.append(local_svd_root)
        if os.path.isdir(core_root):
            search_roots.append(core_root)

        for search_root in search_roots:
            for root, _, files in os.walk(search_root):
                for file in files:
                    if file.lower().endswith(".svd") and file not in SVD_INDEX_CACHE:
                        SVD_INDEX_CACHE[file] = os.path.join(root, file)

    return SVD_INDEX_CACHE.get(svd_basename)


def build_remote_svd_urls(svd_file_value):
    # boards_entry uses paths like .../svd/STM32WBAxx/STM32WBA52.svd
    urls = []
    parts = svd_file_value.replace("\\", "/").split("/")
    svd_basename = os.path.basename(svd_file_value)

    family_dir = ""
    if "svd" in parts:
        svd_index = parts.index("svd")
        if svd_index + 1 < len(parts):
            family_dir = parts[svd_index + 1]

    if family_dir and svd_basename:
        urls.append(f"https://raw.githubusercontent.com/cmsis-svd/cmsis-svd/main/data/STMicro/{family_dir}/{svd_basename}")

    if svd_basename:
        urls.append(f"https://raw.githubusercontent.com/cmsis-svd/cmsis-svd/main/data/STMicro/{svd_basename}")

    return dedupe_preserve_order(urls)


def fetch_remote_svd_content(svd_file_value):
    for url in build_remote_svd_urls(svd_file_value):
        if url in SVD_CONTENT_CACHE:
            return SVD_CONTENT_CACHE[url]

        try:
            with urllib.request.urlopen(url, timeout=8) as response:
                content = response.read().decode("utf-8", errors="ignore")
                SVD_CONTENT_CACHE[url] = content
                return content
        except (urllib.error.URLError, TimeoutError, ValueError):
            continue

    return None


def get_svd_content(core_root, svd_file_value):
    svd_path = find_svd_file_in_repo(core_root, svd_file_value)
    cache_key = svd_path if svd_path else f"remote::{svd_file_value}"

    if cache_key in SVD_CONTENT_CACHE:
        return SVD_CONTENT_CACHE[cache_key], cache_key

    content = None
    if svd_path:
        with open(svd_path, "r", encoding="utf-8", errors="ignore") as file:
            content = file.read()
    else:
        content = fetch_remote_svd_content(svd_file_value)

    SVD_CONTENT_CACHE[cache_key] = content
    return content, cache_key


def parse_bool_text(value):
    return str(value).strip().lower() in ["1", "true", "yes"]


def format_cortex_name(cpu_name):
    core = cpu_name.strip().upper().replace("+", "PLUS")
    if core.startswith("CM"):
        return f"Cortex-M{core[2:].replace('PLUS', '+')}"
    if core.startswith("CA"):
        return f"Cortex-A{core[2:]}"
    return cpu_name.strip()


def parse_svd_cpu_profile(core_root, svd_file_value):
    content, _ = get_svd_content(core_root, svd_file_value)
    if not content:
        return {"cortex": "-", "fpu": "-", "cpu_topology": "-"}

    cpu_match = re.search(r"<cpu>(.*?)</cpu>", content, re.DOTALL)
    if not cpu_match:
        return {"cortex": "-", "fpu": "-", "cpu_topology": "-"}

    cpu_block = cpu_match.group(1)

    name_match = re.search(r"<name>\s*([^<]+)\s*</name>", cpu_block)
    fpu_match = re.search(r"<fpuPresent>\s*([^<]+)\s*</fpuPresent>", cpu_block)

    cortex = format_cortex_name(name_match.group(1).strip()) if name_match else "-"
    fpu = "Yes" if (fpu_match and parse_bool_text(fpu_match.group(1))) else "No"
    return {"cortex": cortex, "fpu": fpu, "cpu_topology": infer_cpu_topology(core_root, svd_file_value)}


def infer_cpu_topology(core_root, svd_file_value):
    svd_basename = os.path.basename(svd_file_value)
    if not svd_basename:
        return "-"

    # Ensure SVD index is populated.
    find_svd_file_in_repo(core_root, svd_file_value)
    if not SVD_INDEX_CACHE:
        return "-"

    stem = os.path.splitext(svd_basename)[0]
    split_match = re.match(r"(.+)_CM[0-9A-ZP]+$", stem, re.IGNORECASE)
    if not split_match:
        return "Single CPU"

    prefix = split_match.group(1)
    cores = []
    for candidate in SVD_INDEX_CACHE.keys():
        candidate_stem = os.path.splitext(candidate)[0]
        core_match = re.match(rf"{re.escape(prefix)}_(CM[0-9A-ZP]+)$", candidate_stem, re.IGNORECASE)
        if core_match:
            cores.append(core_match.group(1).upper())

    cores = dedupe_preserve_order(cores)
    if len(cores) > 1:
        return f"Dual CPU ({'/'.join(cores)})"
    return "Single CPU"


def summarize_cortex(board_entries, core_root):
    cortex_values = []
    for entry in board_entries:
        svd_file = entry.get("svd_file", "")
        if not svd_file:
            continue
        profile = parse_svd_cpu_profile(core_root, svd_file)
        if profile["cortex"] != "-":
            cortex_values.append(profile["cortex"])
    cortex_values = dedupe_preserve_order(cortex_values)
    return "<br>".join(cortex_values) if cortex_values else "-"


def summarize_fpu(board_entries, core_root):
    fpu_values = []
    for entry in board_entries:
        svd_file = entry.get("svd_file", "")
        if not svd_file:
            continue
        profile = parse_svd_cpu_profile(core_root, svd_file)
        if profile["fpu"] != "-":
            fpu_values.append(profile["fpu"])
    fpu_values = dedupe_preserve_order(fpu_values)
    return "/".join(fpu_values) if fpu_values else "-"


def detect_subfamily_features(subfamily_path, board_entries):
    features = {
        "wireless": "No",
        "usb": "No",
        "can": "No",
        "eth": "No"
    }

    product_lines = " ".join([entry.get("product_line", "") for entry in board_entries]).upper()
    path_hint = subfamily_path.upper()
    if any(token in product_lines or token in path_hint for token in ["STM32WB", "STM32WL", "STM32WBA"]):
        features["wireless"] = "Yes"

    peripheral_pins_path = os.path.join(subfamily_path, "PeripheralPins.c")
    if os.path.isfile(peripheral_pins_path):
        with open(peripheral_pins_path, "r", encoding="utf-8", errors="ignore") as file:
            content = file.read()

        if "PinMap_USB_" in content or "PinMap_OTG_" in content or "USB_DM" in content or "USB_DP" in content:
            features["usb"] = "Yes"
        if "PinMap_CAN_" in content or "PinMap_FDCAN_" in content:
            features["can"] = "Yes"
        if "PinMap_ETH_" in content:
            features["eth"] = "Yes"

    return features


def summarize_cpu_topology(board_entries, core_root):
    topology_values = []
    for entry in board_entries:
        svd_file = entry.get("svd_file", "")
        if not svd_file:
            continue
        profile = parse_svd_cpu_profile(core_root, svd_file)
        if profile["cpu_topology"] != "-":
            topology_values.append(profile["cpu_topology"])
    topology_values = dedupe_preserve_order(topology_values)
    return "<br>".join(topology_values) if topology_values else "-"

def extract_pins_from_variant(variant_file):
    # Read the content of the variant file
    with open(variant_file, "r") as file:
        variant_content = file.read()
        # Remove commented lines
        variant_content = re.sub(r'^\s*\/\/.*\n', '', variant_content)
        # Regular expression pattern to extract pin information
        pin_pattern = r"^\s*(\w+),?\s*(?:\/\/\s*(.+))?$"
        # Find all matches of the pattern in the variant content
        matches = re.findall(pin_pattern, variant_content, re.MULTILINE)
        # Filter out empty matches
        matches = [(pin, name if name else pin) for index, (pin, name) in enumerate(matches, start=1) if pin and not pin.startswith("//")]
        return matches
       
def generate_timer_pin_table(file_path, variant_files):
    # Read the content of the header file
    with open(file_path, "r") as file:
        header_content = file.read()
        # Regular expression pattern to extract pin, timer, and channel information
        pattern = r"{(\w+),\s+(\w+),\s+STM_PIN_DATA_EXT\(\w+,\s+\w+,\s+\w*AF\w+,\s+(\d+),\s+(\d+)\)}"
        # Find all matches of the pattern in the header content
        matches = re.findall(pattern, header_content)
        # Initialize table rows
        table_rows = []
        alternatives_rows = {}
        # Process each match and populate the table rows
        for match in matches:
            pin, timer, channel, inverted = match
            if "ALT" in pin: 
                pin, alt = pin.split("_ALT")
                if pin not in alternatives_rows:
                    alternatives_rows[pin] = []
                alternatives_rows[pin].append([alt, timer, channel + ("N" if inverted == "1" else "")])
                continue
            # if inverted add letter "N" to the channel
            table_rows.append([pin, timer, channel + ("N" if inverted == "1" else "")])
        
        # Process variant files
        for variant_file in variant_files:
            variant_pins = ({name: pin for name, pin in extract_pins_from_variant(variant_file)})
            
            # Update table rows with variant pins
            for row in table_rows:
                pin = row[0]
                if pin in variant_pins:
                    row.append(variant_pins[pin])
                else:
                    row.append("-")
        return table_rows, alternatives_rows

def generate_adc_pin_table(file_path, variant_files):
    # Read the content of the header file
    with open(file_path, "r") as file:
        header_content = file.read()
        # Regular expression pattern to extract pin, timer, and channel information
        pattern = r"{(\w+),\s+(\w+),\s+STM_PIN_DATA_EXT\(\w+,\s+\w+,\s+(\d+),\s+(\d+),\s+(\d+)\)}"
        # Find all matches of the pattern in the header content
        matches = re.findall(pattern, header_content)
        # Initialize table rows
        table_rows = []
        alternatives_rows = {}
        # Process each match and populate the table rows
        for match in matches:
            pin, adc, _, channel, _ = match
            # if adc is not "ADCx" remove
            if adc[:3] == "ADC":  
                if "ALT" in pin: 
                    pin, alt = pin.split("_ALT")
                    if pin not in alternatives_rows:
                        alternatives_rows[pin] = []
                    alternatives_rows[pin].append([alt, adc, channel])
                    continue
                table_rows.append([pin, adc, channel])
        
        # Process variant files
        for variant_file in variant_files:
            variant_pins = ({name: pin for name, pin in extract_pins_from_variant(variant_file)})
            
            # Update table rows with variant pins
            for row in table_rows:
                pin = row[0]
                if pin in variant_pins:
                    row.append(variant_pins[pin])
                else:
                    row.append("-")

        return table_rows, alternatives_rows


def generate_interface_pin_table(file_path, variant_files, pinmap_definitions):
    # Read PeripheralPins.c content and extract selected PinMap_* blocks.
    with open(file_path, "r") as file:
        header_content = file.read()

    table_rows = []
    alternatives_rows = {}
    entry_pattern = r"\{\s*([A-Z0-9_]+)\s*,\s*([A-Z0-9_]+)\s*,\s*STM_PIN_DATA(?:_EXT)?\([^{};]*\)\s*\}"

    for signal_name, pinmap_name in pinmap_definitions:
        block_pattern = rf"PinMap_{re.escape(pinmap_name)}\s*\[\]\s*=\s*\{{(.*?)\}};"
        blocks = re.findall(block_pattern, header_content, re.DOTALL)

        for block in blocks:
            matches = re.findall(entry_pattern, block)
            for pin, peripheral in matches:
                if "ALT" in pin:
                    pin, alt = pin.split("_ALT")
                    if pin not in alternatives_rows:
                        alternatives_rows[pin] = []
                    alternatives_rows[pin].append([alt, peripheral, signal_name])
                    continue
                table_rows.append([pin, peripheral, signal_name])

    # Process variant files
    for variant_file in variant_files:
        variant_pins = ({name: pin for name, pin in extract_pins_from_variant(variant_file)})

        # Update table rows with variant pins
        for row in table_rows:
            pin = row[0]
            if pin in variant_pins:
                row.append(variant_pins[pin])
            else:
                row.append("-")

    return table_rows, alternatives_rows



def process_family(family_path, family_name):
    timer_info = []
    adc_info = []
    uart_info = []
    spi_info = []
    i2c_info = []
    can_info = []
    subfamilies = []
    variant_names = []
    for root, dirs, files in os.walk(family_path):
        variant_files = [os.path.join(root, f) for f in files if f.startswith("variant_") and f.endswith(".cpp")]
        # set the generic variant first
        variant_files = sorted(variant_files, key=lambda x: "generic" not in x)
        variant_names = [os.path.basename(f).replace("variant_", "").replace(".cpp", "") for f in variant_files]
        for file in files:
            if file.endswith('PeripheralPins.c'):
                # Generate pin tables from header files
                timer_info.append(generate_timer_pin_table(os.path.join(root, file), variant_files))
                # Generate pin tables from header files
                adc_info.append(generate_adc_pin_table(os.path.join(root, file), variant_files))
                uart_info.append(generate_interface_pin_table(
                    os.path.join(root, file),
                    variant_files,
                    [
                        ("TX", "UART_TX"),
                        ("RX", "UART_RX"),
                        ("RTS", "UART_RTS"),
                        ("CTS", "UART_CTS"),
                        ("DE", "UART_DE")
                    ]
                ))
                spi_info.append(generate_interface_pin_table(
                    os.path.join(root, file),
                    variant_files,
                    [
                        ("MOSI", "SPI_MOSI"),
                        ("MISO", "SPI_MISO"),
                        ("SCLK", "SPI_SCLK"),
                        ("NSS", "SPI_NSS"),
                        ("SSEL", "SPI_SSEL")
                    ]
                ))
                i2c_info.append(generate_interface_pin_table(
                    os.path.join(root, file),
                    variant_files,
                    [
                        ("SDA", "I2C_SDA"),
                        ("SCL", "I2C_SCL"),
                        ("SMBA", "I2C_SMBA")
                    ]
                ))
                can_info.append(generate_interface_pin_table(
                    os.path.join(root, file),
                    variant_files,
                    [
                        ("RX", "CAN_RX"),
                        ("TX", "CAN_TX"),
                        ("RD", "CAN_RD"),
                        ("TD", "CAN_TD"),
                        ("RX", "FDCAN_RX"),
                        ("TX", "FDCAN_TX")
                    ]
                ))
        for subdir in dirs:
            subfamily_path = os.path.join(family_name, sanitize_filename(subdir))
            subfamilies.append(subfamily_path)
    return timer_info, adc_info, uart_info, spi_info, i2c_info, can_info, subfamilies, variant_names

def generate_collapsible_table(rows, headers):
    html_table = "<table>\n"
    html_table += "<thead>\n<tr>\n"
    for header in headers:
        html_table += f"<th markdown='1'>{header}</th>\n"
    html_table += "</tr>\n</thead>\n<tbody>\n"

    for subfamily_pins, alternative_pins in rows:
         for pin_index, pin in enumerate(subfamily_pins):
            if alternative_pins.get(pin[0]) is not None:
                no_alt = len(alternative_pins[pin[0]])
                html_table += f"<tr id='pin_{pin_index}'  class='clickable_pin'>\n<td ><b>{pin[0]}</b> (no. alternatives: {no_alt})</td>\n<td>{pin[1]}</td>\n<td>{pin[2]}</td>\n"
                for data in pin[3:]:
                    html_table += f"<td>{data}</td>\n"
                html_table += "</tr>\n"
                for alt in alternative_pins[pin[0]]:
                    html_table += f"<tr class='collapsible_pin toggle_pin_{pin_index} hide_alt'>\n<td>{pin[0]}_ALT{alt[0]}</td>\n"
                    for data in alt[1:]:
                        html_table += f"<td>{data}</td>\n"
                    html_table += "</tr>\n"
            else:
                html_table += f"<tr>\n<td><b>{pin[0]}</b></td>\n<td>{pin[1]}</td>\n<td>{pin[2]}</td>\n"
                for data in pin[3:]:
                    html_table += f"<td>{data}</td>\n"
                html_table += "</tr>\n"
    
    html_table += "</tbody>\n</table>"
    
    return html_table


# Path to the directory containing family folders
local_svd_root = 'stm32_svd'
core_root = 'Arduino_Core_STM32'
families_path = 'Arduino_Core_STM32/variants/'
url_to_repo = 'https://github.com/stm32duino/Arduino_Core_STM32/blob/2.12.0/variants'

# Create a main page to list all family-specific main pages
main_page_content = []

print("Processing families...")
# Processing each family folder grouped by first STM32 letter (F/G/L/...)
family_folders = [name for name in os.listdir(families_path) if os.path.isdir(os.path.join(families_path, name))]


def family_group_letter(family_name):
    match = re.match(r"^STM32([A-Z])", family_name)
    return match.group(1) if match else "Z"


def family_sort_key_within_group(family_name, group_letter):
    # Example: STM32F4xx -> remainder "4xx"; STM32MP1xx -> remainder "P1xx"
    prefix = f"STM32{group_letter}"
    remainder = family_name[len(prefix):]
    num_match = re.search(r"(\d+)", remainder)
    if num_match:
        number = int(num_match.group(1))
        text_prefix = remainder[:num_match.start()]
        text_suffix = remainder[num_match.end():]
    else:
        number = 10**9
        text_prefix = remainder
        text_suffix = ""
    return (number, text_prefix, text_suffix, family_name)


families_by_group = {}
for family in family_folders:
    group_letter = family_group_letter(family)
    if group_letter not in families_by_group:
        families_by_group[group_letter] = []
    families_by_group[group_letter].append(family)

group_letters = sorted(families_by_group.keys())

# Generate group index pages (STM32F, STM32G, ...)
for group_order, group_letter in enumerate(group_letters, start=1):
    group_title = f"STM32{group_letter}"
    group_folder = sanitize_filename(group_title)
    os.makedirs(group_folder, exist_ok=True)
    group_families = sorted(
        families_by_group[group_letter],
        key=lambda family_name: family_sort_key_within_group(family_name, group_letter)
    )

    group_index = os.path.join(group_folder, "index.md")
    with open(group_index, 'w') as gf:
        gf.write('---\n')
        gf.write('layout: default\n')
        gf.write('parent: STM32 Family Pinout\n')
        gf.write(f'title: {group_title}\n')
        gf.write(f'nav_order: {group_order}\n')
        gf.write('has_children: true\n')
        gf.write('has_toc: false\n')
        gf.write('---\n\n')
        gf.write(f"# {group_title} Families\n\n")
        gf.write("## Families\n\n")
        gf.write("<table class='subfamily-table'>\n")
        gf.write("<thead><tr><th>Family</th></tr></thead>\n")
        gf.write("<tbody>\n")
        for family_name in group_families:
            family_folder_name = sanitize_filename(family_name)
            gf.write(f"<tr><td><a href='{family_folder_name}/'>{family_name}</a></td></tr>\n")
        gf.write("</tbody>\n</table>\n")

for group_letter in group_letters:
    group_title = f"STM32{group_letter}"
    group_folder = sanitize_filename(group_title)
    group_families = sorted(
        families_by_group[group_letter],
        key=lambda family_name: family_sort_key_within_group(family_name, group_letter)
    )

    for family_order, family_folder in enumerate(group_families, start=1):
        family_path = os.path.join(families_path, family_folder)
        if not os.path.isdir(family_path):
            continue

        # Create a folder for each family to store subfamily markdown files
        family_output_folder = os.path.join(group_folder, sanitize_filename(family_folder))
        os.makedirs(family_output_folder, exist_ok=True)
        
        # Create a main page for the family
        family_main_page = os.path.join(family_output_folder, "index.md")
        
        with open(family_main_page, 'w') as f:
            # Writing Jekyll front matter
            f.write('---\n')
            f.write('layout: default\n')
            f.write('grand_parent: STM32 Family Pinout\n')
            f.write(f'parent: {group_title}\n')
            f.write(f'title: {family_folder}\n')
            f.write(f'nav_order: {family_order}\n')
            f.write('has_children: true\n')
            f.write('has_toc: false\n')
            f.write('---\n\n')
            
            f.write(f"# {family_folder} Family\n\n")
            f.write("## Subfamilies\n\n")
            f.write("Use browser search (`Ctrl+F`) by subfamily name in the table below.\n\n")
            
            timer_info, adc_info, uart_info, spi_info, i2c_info, can_info, subfamilies, _ = process_family(family_path, family_output_folder)
            expanded_rows_count = 0

            f.write("<table class='subfamily-table'>\n")
            f.write("<thead><tr><th>Subfamily</th><th>Example Variants</th><th>Product Line</th><th>Flash</th><th>RAM</th><th>Cortex</th><th>FPU</th><th>CPU</th><th>CAN/FDCAN</th></tr></thead>\n")
            f.write("<tbody>\n")
            
            for subfamily in sorted(subfamilies, key=lambda p: format_display_name(os.path.basename(p))):
                # get variants for this subfamily
                subfamily_path = os.path.join(family_path, os.path.basename(subfamily))
                # print(subfamily_path)
                _, _, _, _, _, _, _, variant_names = process_family(subfamily_path, family_output_folder)
                # remove generic from the variant names
                variant_names = [name for name in variant_names if name != "generic"]
                board_entries = parse_boards_entry_file(subfamily_path)
                features = detect_subfamily_features(subfamily_path, board_entries)
                # use only the subfamily name using os package
                subfamily1 = os.path.basename(subfamily)

                # Add one row per sub-sub-family token, all linking to the same pinout page.
                for row_name in expand_subfamily_rows(subfamily1):
                    subfamily_display_name = format_display_name(row_name)
                    row_variants = filter_variants_for_row(row_name, variant_names)
                    row_board_entries = filter_board_entries_for_row(row_name, board_entries)
                    variants_md = ", ".join(row_variants) if row_variants else "-"
                    row_product_lines = summarize_product_lines(row_board_entries)
                    row_flash = summarize_flash_sizes(row_board_entries)
                    row_ram = summarize_ram_sizes(row_board_entries)
                    cpu_entries = row_board_entries if row_board_entries else board_entries
                    row_cortex = summarize_cortex(cpu_entries, core_root)
                    row_fpu = summarize_fpu(cpu_entries, core_root)
                    row_cpu = summarize_cpu_topology(cpu_entries, core_root)
                    f.write(f"<tr><td><a href='{subfamily1}/pinout'>{subfamily_display_name}</a></td><td>{variants_md}</td><td>{row_product_lines}</td><td>{row_flash}</td><td>{row_ram}</td><td>{row_cortex}</td><td>{row_fpu}</td><td>{row_cpu}</td><td>{features['can']}</td></tr>\n")
                    expanded_rows_count += 1
                # Create subfamily folder
                os.makedirs(os.path.join(subfamily), exist_ok=True)

            f.write("</tbody>\n</table>\n\n")
            f.write(f"<small>Expanded {expanded_rows_count} searchable subfamilies from {len(subfamilies)} grouped folders.</small>\n")
            
            # Add link to the main page
            f.write("\n\n[Back to Main Page](../)")
        
        # Process each subfamily
        for subfamily_folder in sorted(os.listdir(family_path)):
            subfamily_path = os.path.join(family_path, subfamily_folder)
            if os.path.isdir(subfamily_path):
                # Generate pin tables for the subfamily
                timer_info, adc_info, uart_info, spi_info, i2c_info, can_info, _, variant_names = process_family(subfamily_path, family_output_folder)

                # replace the variant names with the link to the variant file
                variant_names = [f"[{name}]({url_to_repo}/{family_folder}/{subfamily_folder}/variant_{name}.cpp)" for name in variant_names]

                # rename the generic variant to the subfamily name
                variant_names = [name.replace("[generic]", "[Generic label]") for name in variant_names]


                # Create a markdown file for the subfamily
                subfamily_markdown_file = os.path.join(family_output_folder, sanitize_filename(subfamily_folder), "pinout.md")
                with open(subfamily_markdown_file, 'w') as f:
                    subfamily_display_name = format_display_name(subfamily_folder)
                    board_entries = parse_boards_entry_file(subfamily_path)
                    # Writing Jekyll front matter
                    f.write('---\n')
                    f.write('layout: default\n')
                    f.write('grand_parent: STM32 Family Pinout\n')
                    f.write(f'parent: {family_folder}\n') 
                    f.write(f'title: {subfamily_display_name} Pinout\n')
                    f.write('has_toc: false\n')
                    f.write('has_children: false\n')
                    f.write('nav_exclude: false\n')
                    f.write('toc: true\n')
                    f.write('---\n\n')

                    aliases = []
                    aliases.extend(build_search_aliases(subfamily_folder))
                    for row_name in expand_subfamily_rows(subfamily_folder):
                        aliases.extend(build_search_aliases(row_name))
                    aliases = dedupe_preserve_order(aliases)
                    aliases_md = ", ".join([f"`{alias}`" for alias in aliases])
                    f.write(f"**Search aliases (Ctrl+F):** {aliases_md}\n\n")

                    if board_entries:
                        features = detect_subfamily_features(subfamily_path, board_entries)
                        f.write("## Board Entry Info\n\n")
                        f.write("<table>\n")
                        f.write("<thead><tr><th>Generic Board</th><th>Pkg</th><th>Product Line</th><th>Flash</th><th>RAM</th><th>Cortex</th><th>FPU</th><th>CPU</th><th>Wireless</th><th>USB</th><th>CAN/FDCAN</th><th>ETH</th><th>SVD</th></tr></thead>\n")
                        f.write("<tbody>\n")
                        for entry in board_entries:
                            label = entry["label"] if entry["label"] else entry["board_id"]
                            pkg_code = infer_package_code(entry["board_id"])
                            product_line = entry["product_line"] if entry["product_line"] else "-"
                            flash = format_size_from_bytes(entry["flash_bytes"])
                            ram = format_size_from_bytes(entry["ram_bytes"])
                            svd_profile = parse_svd_cpu_profile(core_root, entry.get("svd_file", ""))
                            entry_cortex = svd_profile["cortex"]
                            entry_fpu = svd_profile["fpu"]
                            entry_cpu = svd_profile["cpu_topology"]
                            svd = os.path.basename(entry["svd_file"]) if entry["svd_file"] else "-"
                            f.write(f"<tr><td>{label}</td><td>{pkg_code}</td><td>{product_line}</td><td>{flash}</td><td>{ram}</td><td>{entry_cortex}</td><td>{entry_fpu}</td><td>{entry_cpu}</td><td>{features['wireless']}</td><td>{features['usb']}</td><td>{features['can']}</td><td>{features['eth']}</td><td>{svd}</td></tr>\n")
                        f.write("</tbody>\n</table>\n\n")
                                        
                    f.write(f" See more info in the [STM32duino repository]({url_to_repo}/{family_folder}/{subfamily_folder}/PeripheralPins.c)\n\n")

                    f.write("## PWM Timer Pins\n\n")


                    table_headers = ["Pin", "PWM Timer", "Channel"]
                    table_headers += variant_names
                    
                    # Markdown table formatting
                    html_table =  html_content = generate_collapsible_table(timer_info, table_headers)
                    f.write(html_table)
                    f.write('\n\n')

                        
                    f.write("## ADC Pins\n\n")
                    table_headers = ["Pin", "ADC", "Channel"]
                    table_headers += variant_names
                    html_table =  html_content = generate_collapsible_table(adc_info, table_headers)
                    f.write(html_table)
                    f.write('\n\n')

                    if any(subfamily_pins for subfamily_pins, _ in uart_info):
                        f.write("## UART Pins\n\n")
                        table_headers = ["Pin", "Peripheral", "Signal"]
                        table_headers += variant_names
                        html_table = generate_collapsible_table(uart_info, table_headers)
                        f.write(html_table)
                        f.write('\n\n')

                    if any(subfamily_pins for subfamily_pins, _ in spi_info):
                        f.write("## SPI Pins\n\n")
                        table_headers = ["Pin", "Peripheral", "Signal"]
                        table_headers += variant_names
                        html_table = generate_collapsible_table(spi_info, table_headers)
                        f.write(html_table)
                        f.write('\n\n')

                    if any(subfamily_pins for subfamily_pins, _ in i2c_info):
                        f.write("## I2C Pins\n\n")
                        table_headers = ["Pin", "Peripheral", "Signal"]
                        table_headers += variant_names
                        html_table = generate_collapsible_table(i2c_info, table_headers)
                        f.write(html_table)
                        f.write('\n\n')

                    if any(subfamily_pins for subfamily_pins, _ in can_info):
                        f.write("## CAN Pins\n\n")
                        table_headers = ["Pin", "Peripheral", "Signal"]
                        table_headers += variant_names
                        html_table = generate_collapsible_table(can_info, table_headers)
                        f.write(html_table)
                        f.write('\n\n')

                    # # Write timer information
                    # for subfamily_pins, alternative_pins in timer_info:
                    #     # Markdown table formatting
                    #     markdown_table = "| " + " | ".join(table_headers) + " |\n"
                    #     markdown_table += "| " + " | ".join(["---"] * len(table_headers)) + " |\n"
                    #     for pin in subfamily_pins:
                    #         markdown_table += "| " + " | ".join(pin) + " |\n"
                    #         # check if key (pin) exist 
                    #         if alternative_pins.get(pin[0]):
                    #             for alt in alternative_pins[pin[0]]:
                    #                     markdown_table += "| " + pin[0]+"_ALT" +(" | ").join(alt) + " |\n"
                    #     f.write(markdown_table)
                    #     f.write('\n\n')
                
                    # f.write("## ADC Pins\n\n")
                    # table_headers = ["Pin", "ADC", "Channel"]
                    # table_headers += variant_names
                    
                    # # # Write timer information
                    # for subfamily_pins, alternative_pins in adc_info:
                    #     # Markdown table formatting
                    #     html_table =  html_content = generate_collapsible_table(adc_info, table_headers)
                    #     f.write(html_table)
                    #     f.write('\n\n')

                    # # Write timer information
                    # for subfamily_timers in adc_info:
                    #     # Markdown table formatting
                    #     markdown_table = "| " + " | ".join(table_headers) + " |\n"
                    #     markdown_table += "| " + " | ".join(["---"] * len(table_headers)) + " |\n"
                    #     for row in subfamily_timers:
                    #         markdown_table += "| " + " | ".join(row) + " |\n"
                    #     f.write(markdown_table)
                    #     f.write('\n\n')
                    
                    # Add link to the main page
                    f.write("[Back to Main Page](../../)")
                    
                    f.write("")

                    # Append subfamily markdown file to family section
                    main_page_content.append(f"- [{subfamily_folder}]({family_output_folder}/{sanitize_filename(subfamily_folder)}/pinout)")

# Write main page content
with open('index.md', 'w') as main_page_file:
    # Writing Jekyll front matter
    main_page_file.write('---\n')
    main_page_file.write('layout: home\n')
    main_page_file.write('title: STM32 Family Pinout\n')
    main_page_file.write('has_children: true\n')
    main_page_file.write('has_toc: false\n')
    main_page_file.write('---\n\n')

    main_page_file.write('# STM32 Family Pinout\n\n')
    main_page_file.write('This page contains a list of pinout information for each subfamily of STM32 variants.\n\n')

    main_page_file.write("This page is automatically generated from the [STM32duino](https://github.com/stm32duino/Arduino_Core_STM32) repository. This webpage has been generated using version [2.12.0](https://github.com/stm32duino/Arduino_Core_STM32/releases).")

    main_page_file.write('\n\n')
    main_page_file.write(f"This page is inteded to be used for quick search of pins for a given STM32 family and subfamily. The main information provided on the pages is the available: \n - **PWM timers** \n - **ADC channels** \n - UART pins \n - SPI pins \n - I2C pins \n - CAN pins\n\n")
    main_page_file.write("The information is extracted from the `PeripheralPins.c` file of the STM32duino repository. ")
    main_page_file.write("The `variant_*.cpp` files are used to provide the variant names for each subfamily. ")
    main_page_file.write("The `variant_generic.cpp` file is used as a generic variant for each subfamily. ")

    main_page_file.write('\n\n')

    main_page_file.write('## How to Use It\n\n')
    main_page_file.write('1. Navigate to the STM32 family and subfamily of interest using the provided links.\n')
    main_page_file.write('2. Click on the subfamily link to view the pinout information for that specific STM32 variant.\n')
    main_page_file.write('3. Use the provided information to identify available PWM timers and ADC channels for your project.\n')
    
    main_page_file.write("\n\n\
<table class='subfamily-table'>\
<thead><tr><th>Family</th></tr></thead>\
<tbody>\
<tr><td><a href='STM32C/'>STM32C</a></td></tr>\
<tr><td><a href='STM32F/'>STM32F</a></td></tr>\
<tr><td><a href='STM32G/'>STM32G</a></td></tr>\
<tr><td><a href='STM32H/'>STM32H</a></td></tr>\
<tr><td><a href='STM32L/'>STM32L</a></td></tr>\
<tr><td><a href='STM32M/'>STM32M</a></td></tr>\
<tr><td><a href='STM32U/'>STM32U</a></td></tr>\
<tr><td><a href='STM32W/'>STM32W</a></td></tr>\
</tbody>\
</table>\
")
    
    main_page_file.write('\n\n')
    
    main_page_file.write('## Contributing\n\n')
    main_page_file.write('This page is automatically generated using a Python script. ')
    main_page_file.write('The script is available in the [GitHub repository](https://github.com/simplefoc/mcupinouts). ')
    main_page_file.write('Please feel free to contribute to the script if you find any issues or have any suggestions. ')