'''
Process all *.html files in specified directories to capture common sections from the newest and 
replace the equivalent sections in all other files.

The common sections are delimited by a html comment tag like <!--FINCLUDE:xxx-->section content<!--FINCLUDE--> 
where xxx can be any name for the section.

All the sections identified in the newest file will be searched and replaced in all other files
within the same directory. When there are more than one section with the same name in the newest file, 
last occurrence will prevail.
'''

import os
import sys
from pathlib import Path

# Array of directories to process
directories = [
    "./Site",
    "./Site/pt",
]

def extract(raw_string, start_marker, end_marker):
    '''
    Extracts a string snippet between two string markers
    '''
    start = raw_string.index(start_marker) + len(start_marker)
    end = raw_string.index(end_marker, start)
    return raw_string[start:end]

def get_html_files(directory):
    '''
    Collects all .html files from a specific directory
    Returns list of tuples (filepath, modification_time)
    '''
    dir_path = Path(directory).resolve()
    if not dir_path.exists():
        print(f"WARNING: Directory not found: {directory}")
        return []
    
    files = [(str(f), os.path.getmtime(f)) 
             for f in dir_path.glob("*.html") 
             if f.is_file()]
    
    return sorted(files, key=lambda f: f[1], reverse=True)

def extract_sections(filename):
    '''
    Processes a file to extract all FINCLUDE sections
    Returns dictionary of section_name: section_content
    '''
    sections = {}
    opened = False
    
    with open(filename) as openfile:
        for line in openfile:
            if not opened:
                if line.strip().startswith("<!--FINCLUDE:"):
                    opened = True
                    section_name = extract(line, "<!--FINCLUDE:", "-->")
                    sections[section_name] = line
            else:
                sections[section_name] += line
                if line.strip().startswith("<!--FINCLUDE-->"):
                    opened = False
    
    return sections

def process_file(filename, sections):
    '''
    Processes a file to replace sections with newest versions
    Returns (new_content, original_content, sections_found)
    '''
    opened = False
    fcontent = ""
    foriginal_content = ""
    sections_found = []
    
    with open(filename) as openfile:
        for line in openfile:
            foriginal_content += line
            if not opened:
                if line.strip().startswith("<!--FINCLUDE:"):
                    section_name = extract(line, "<!--FINCLUDE:", "-->")
                    if section_name in sections:
                        opened = True
                        sections_found.append(section_name)
                        fcontent += sections[section_name]
                    else:
                        fcontent += line
                else:
                    fcontent += line
            else:
                if line.strip().startswith("<!--FINCLUDE-->"):
                    opened = False
    
    return fcontent, foriginal_content, sections_found

def process_directory(directory):
    '''
    Process all HTML files in a single directory
    '''
    print(f"\n--- Processing directory: {directory}")
    
    # Get all HTML files in this directory
    files = get_html_files(directory)
    if not files:
        print(f"No HTML files found in directory: {directory}")
        return
    
    # Process the newest file to collect sections
    newest_file = files[0][0]
    sections = extract_sections(newest_file)
    
    print(f"NEWEST: {newest_file} HAS {len(sections)} SECTIONS: {sections.keys()}")
    
    # Process all other files in this directory
    files_nosection, files_updated, files_nochange = [], [], []
    
    for fname, ftime in files[1:]:
        fcontent, foriginal_content, sections_found = process_file(fname, sections)
        
        if len(sections_found) > 0:
            if fcontent == foriginal_content:
                files_nochange.append(fname)
            else:
                with open(fname, "w") as f:
                    f.write(fcontent)
                files_updated.append(fname)
                print(f"UPDATED: {fname} HAS {len(sections_found)} SECTIONS {sections_found}")
        else:
            files_nosection.append(fname)
    
    print(f"--- Directory Summary: {len(files[1:])}_FOUND = {len(files_updated)}_UPDATED + "
          f"{len(files_nochange)}_NOCHANGE + {len(files_nosection)}_NOSECTION = "
          f"{len(files_updated) + len(files_nochange) + len(files_nosection)}_SUM")

def main():
    print("=== STARTED finclude.py ===")
    
    for directory in directories:
        process_directory(directory)
    
    print("\n=== FINISHED finclude.py ===")

if __name__ == "__main__":
    main()