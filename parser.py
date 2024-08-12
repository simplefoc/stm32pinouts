
import os
import re

def sanitize_filename(name):
    # Replace any invalid characters with underscores
    return re.sub(r'[^\w\-_.() ]', '_', name)

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



def process_family(family_path, family_name):
    timer_info = []
    adc_info = []
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
        for subdir in dirs:
            subfamily_path = os.path.join(family_name, sanitize_filename(subdir))
            subfamilies.append(subfamily_path)
    return timer_info, adc_info, subfamilies, variant_names

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
families_path = 'Arduino_Core_STM32/variants/'
url_to_repo = 'https://github.com/stm32duino/Arduino_Core_STM32/blob/2.7.1/variants'

# Create a main page to list all family-specific main pages
main_page_content = []

print("Processing families...")
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
            f.write('parent: STM32 Family Pinout\n')
            f.write(f'title: {family_folder} Family Pinout\n')
            f.write('has_children: true\n')
            f.write('has_toc: false\n'))
            f.write('---\n\n')
            
            f.write(f"# {family_folder} Family\n\n")
            f.write("## Subfamilies\n\n")
            
            timer_info, adc_info, subfamilies, _ = process_family(family_path, family_output_folder)
            
            for subfamily in subfamilies:
                # get variants for this subfamily
                subfamily_path = os.path.join(family_path, os.path.basename(subfamily))
                # print(subfamily_path)
                _, _, _, variant_names = process_family(subfamily_path, family_output_folder)
                # remove generic from the variant names
                variant_names = [name for name in variant_names if name != "generic"]
                variant_names = ", ".join(variant_names)
                # use only the subfamily name using os package
                subfamily1 = os.path.basename(subfamily)
                f.write(f"- [{subfamily1}]({subfamily1}/pinout) ")
                # add variant names if available
                if variant_names: f.write(f"\| <small> example: {variant_names.replace('generic', '')} </small>")
                f.write("\n")
                # Create subfamily folder
                os.makedirs(os.path.join(subfamily), exist_ok=True)
            
            # Add link to the main page
            f.write("\n\n[Back to Main Page](../)")
        
        # Process each subfamily
        for subfamily_folder in os.listdir(family_path):
            subfamily_path = os.path.join(family_path, subfamily_folder)
            if os.path.isdir(subfamily_path):
                # Generate pin tables for the subfamily
                timer_info, adc_info, _, variant_names = process_family(subfamily_path, family_output_folder)

                # replace the variant names with the link to the variant file
                variant_names = [f"[{name}]({url_to_repo}/{family_folder}/{subfamily_folder}/variant_{name}.cpp)" for name in variant_names]

                # rename the generic variant to the subfamily name
                variant_names = [name.replace("[generic]", "[Generic label]") for name in variant_names]


                # Create a markdown file for the subfamily
                subfamily_markdown_file = os.path.join(family_output_folder, sanitize_filename(subfamily_folder), "pinout.md")
                with open(subfamily_markdown_file, 'w') as f:
                    # Writing Jekyll front matter
                    f.write('---\n')
                    f.write('layout: default\n')
                    f.write('grand_parent: STM32 Family Pinout\n')
                    f.write(f'parent: {family_folder} Family Pinout\n') 
                    f.write(f'title: {subfamily_folder} Pinout\n')
                    f.write('has_toc: false\n')
                    f.write('has_children: false\n')
                    f.write('nav_exclude: true\n')
                    f.write('toc: true\n')
                    f.write('---\n\n')
                                        
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
    main_page_file.write('has_toc: true\n')
    main_page_file.write('---\n\n')

    main_page_file.write('# STM32 Family Pinout\n\n')
    main_page_file.write('This page contains a list of pinout information for each subfamily of STM32 variants.\n\n')

    main_page_file.write("This page is automatically generated from the [STM32duino](https://github.com/stm32duino/Arduino_Core_STM32) repository. This webpage has been generated using version [2.7.1](https://github.com/stm32duino/Arduino_Core_STM32/releases).")

    main_page_file.write('\n\n')
    main_page_file.write("This page is inteded to be used for quick search of available PWM timers and ADC channels for a given STM32 family and subfamily. ")
    main_page_file.write("The information is extracted from the `PeripheralPins.c` file of the STM32duino repository. ")
    main_page_file.write("The `variant_*.cpp` files are used to provide the variant names for each subfamily. ")
    main_page_file.write("The `variant_generic.cpp` file is used as a generic variant for each subfamily. ")

    main_page_file.write('\n\n')

    main_page_file.write('## How to Use It\n\n')
    main_page_file.write('1. Navigate to the STM32 family and subfamily of interest using the provided links.\n')
    main_page_file.write('2. Click on the subfamily link to view the pinout information for that specific STM32 variant.\n')
    main_page_file.write('3. Use the provided information to identify available PWM timers and ADC channels for your project.\n')

    main_page_file.write('\n\n')
    
    main_page_file.write('## Contributing\n\n')
    main_page_file.write('This page is automatically generated using a Python script. ')
    main_page_file.write('The script is available in the [GitHub repository](https://github.com/simplefoc/mcupinouts). ')
    main_page_file.write('Please feel free to contribute to the script if you find any issues or have any suggestions. ')