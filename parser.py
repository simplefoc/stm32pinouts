
import os
import re

def sanitize_filename(name):
    # Replace any invalid characters with underscores
    return re.sub(r'[^\w\-_.() ]', '_', name)

# def extract_pins_from_variant(variant_file):
#     # Read the content of the variant file
#     with open(variant_file, "r") as file:
#         variant_content = file.read()
#         # Regular expression pattern to extract pin information
#         pin_pattern = r"\s*(\w+),?\s+//\s*(.+)*\n"        
#         # Find all matches of the pattern in the variant content
#         matches = re.findall(pin_pattern, variant_content)
#         if not matches or not matches[0][0].startswith("P"):
#             # Regular expression pattern to extract pin information
#             pin_pattern = r"\s+(\w+),?\s*\n"     
#             # Find all matches of the pattern in the variant content
#             matches_tmp = re.findall(pin_pattern, variant_content)   
#             matches = []
#             for m in matches_tmp:
#                 if m[0].startswith("P"):
#                     matches.append((m,m))            
#         return matches
def extract_pins_from_variant(variant_file):
    # Read the content of the variant file
    with open(variant_file, "r") as file:
        variant_content = file.read()
        # Remove commented lines
        variant_content = re.sub(r'^\s+\/\/.*\n', '', variant_content)
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
        # Process each match and populate the table rows
        for match in matches:
            pin, timer, channel, inverted = match
            # if inverted add letter "N" to the channel
            table_rows.append([pin, f"{timer}", channel + ("N" if inverted == "1" else "")])
        
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
        # else:
        #     print("No variant pins found", variant_files, variant_pins,file_path)
        return table_rows

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
        # Process each match and populate the table rows
        for match in matches:
            pin, adc, _, channel, _ = match
            # if adc is not "ADCx" remove
            if adc[:3] == "ADC":  table_rows.append([pin, adc, channel])
        
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

        return table_rows



def process_family(family_path, family_name):
    timer_info = []
    adc_info = []
    subfamilies = []
    variant_names = []
    for root, dirs, files in os.walk(family_path):
        variant_files = [os.path.join(root, f) for f in files if f.startswith("variant_") and f.endswith(".cpp")]
        variant_names = [os.path.basename(f).replace("variant_", "").replace(".cpp", "") for f in variant_files]
        for file in files:
            if file.endswith('PeripheralPins.c'):
                # Generate pin tables from header files
                timer_info.append(generate_timer_pin_table(os.path.join(root, file), variant_files))
                # Generate pin tables from header files
                adc_info.append(generate_adc_pin_table(os.path.join(root, file), variant_files))
        for subdir in dirs:
            subfamily_path = os.path.join(family_name, sanitize_filename(subdir))
            subfamilies.append(subfamily_path)
    return timer_info, adc_info, subfamilies, variant_names

# Path to the directory containing family folders
families_path = '../Arduino_Core_STM32/variants/'

# Create a main page to list all family-specific main pages
main_page_content = []

# Processing each family folder
for family_folder in os.listdir(families_path):
    family_path = os.path.join(families_path, family_folder)
    if os.path.isdir(family_path):
        # Create a folder for each family to store subfamily markdown files
        family_output_folder = sanitize_filename(family_folder)
        os.makedirs(family_output_folder, exist_ok=True)
        
        # Create a main page for the family
        family_main_page = os.path.join(family_output_folder, "index.md")
        
        with open(family_main_page, 'w') as f:
            # Writing Jekyll front matter
            f.write('---\n')
            f.write('layout: default\n')
            f.write(f'title: {family_folder} Family Pinout\n')
            f.write('---\n\n')
            
            # Breadcrumbs
            f.write("[Home](../index.md) / ")
            f.write(f"{family_folder}\n\n")
    
            f.write(f"# {family_folder} Family\n\n")
            f.write("## Subfamilies\n\n")
            
            timer_info, adc_info, subfamilies, _ = process_family(family_path, family_output_folder)
            
            for subfamily in subfamilies:
                # get variants for this subfamily
                subfamily_path = os.path.join(family_path, os.path.basename(subfamily))
                # print(subfamily_path)
                _, _, _, variant_names = process_family(subfamily_path, family_output_folder)
                variant_names = ", ".join(variant_names)
                # use only the subfamily name using os package
                subfamily1 = os.path.basename(subfamily)
                f.write(f"- [{subfamily1}]({subfamily1}/pinout.md) ")
                if variant_names: f.write(f"({variant_names})")
                f.write("\n")
                # Create subfamily folder
                os.makedirs(os.path.join(subfamily), exist_ok=True)
            
            # Add link to the main page
            f.write("\n\n[Back to Main Page](../index.md)")
        
        # Process each subfamily
        for subfamily_folder in os.listdir(family_path):
            subfamily_path = os.path.join(family_path, subfamily_folder)
            if os.path.isdir(subfamily_path):
                # Generate pin tables for the subfamily
                timer_info, adc_info, _, variant_names = process_family(subfamily_path, family_output_folder)
                
                # Create a markdown file for the subfamily
                subfamily_markdown_file = os.path.join(family_output_folder, sanitize_filename(subfamily_folder), "pinout.md")
                with open(subfamily_markdown_file, 'w') as f:
                    # Writing Jekyll front matter
                    f.write('---\n')
                    f.write('layout: default\n')
                    f.write(f'title: {subfamily_folder} Pinout\n')
                    f.write('---\n\n')
                    
                    # Breadcrumbs
                    f.write("[Home](../../index.md) / ")
                    f.write(f"[{family_folder}](../index.md)")
                    f.write(f" / {subfamily_folder}\n\n")
                    
                    
                    f.write("## PWM Timer Pins\n\n")

                    table_headers = ["Pin", "PWM Timer", "Channel"]
                    table_headers += variant_names
                    
                    # Write timer information
                    for subfamily_timers in timer_info:
                        # Markdown table formatting
                        markdown_table = "| " + " | ".join(table_headers) + " |\n"
                        markdown_table += "| " + " | ".join(["---"] * len(table_headers)) + " |\n"
                        for row in subfamily_timers:
                            markdown_table += "| " + " | ".join(row) + " |\n"
                        f.write(markdown_table)
                        f.write('\n\n')
                    
                    f.write("## ADC Pins\n\n")
                    table_headers = ["Pin", "ADC", "Channel"]
                    table_headers += variant_names
                    # Write timer information
                    for subfamily_timers in adc_info:
                        # Markdown table formatting
                        markdown_table = "| " + " | ".join(table_headers) + " |\n"
                        markdown_table += "| " + " | ".join(["---"] * len(table_headers)) + " |\n"
                        for row in subfamily_timers:
                            markdown_table += "| " + " | ".join(row) + " |\n"
                        f.write(markdown_table)
                        f.write('\n\n')
                    
                    # Add link to the main page
                    f.write("[Back to Main Page](../../index.md)")
                    
                    # Append subfamily markdown file to family section
                    main_page_content.append(f"- [{subfamily_folder}]({family_output_folder}/{sanitize_filename(subfamily_folder)}/pinout.md)")

# Write main page content
with open('index.md', 'w') as main_page_file:
    # Writing Jekyll front matter
    main_page_file.write('---\n')
    main_page_file.write('layout: home\n')
    main_page_file.write('title: STM32 Subfamily Pinout\n')
    main_page_file.write('---\n\n')

    main_page_file.write('# STM32 Subfamily Pinout\n\n')
    main_page_file.write('This page contains a list of pinout information for each subfamily of STM32 variants.\n\n')
    main_page_file.write("<ul>\n")

    for family_folder in os.listdir(families_path):
        family_path = os.path.join(families_path, family_folder)
        if os.path.isdir(family_path):
            # main_page_file.write(f"<a href='{sanitize_filename(family_folder)}/index.md'>{family_folder}</a>\n")
            
            main_page_file.write("<details>\n")
            main_page_file.write(f"<summary><a href='{sanitize_filename(family_folder)}/index.md'>{family_folder}</a></summary>\n")
            main_page_file.write("<ul>\n")

            
            _, _, subfamilies, _ = process_family(family_path, family_folder)
            
            for subfamily in subfamilies:
                main_page_file.write(f"<li><a href='{subfamily}/pinout.md'>{os.path.basename(subfamily)}</a></li>\n")
            
            main_page_file.write("</ul>\n")
            main_page_file.write("</details>\n")
            main_page_file.write("</li>\n")

    main_page_file.write("</ul>\n")
