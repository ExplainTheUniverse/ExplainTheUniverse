import markdown
import re
from pathlib import Path
from bs4 import BeautifulSoup

def md_to_html(md_content):
    # Convert Markdown to HTML
    html = markdown.markdown(md_content, extensions=['extra'])
    
    # Replace heading tags with appropriate classes
    html = re.sub(r'<h1>(.*?)</h1>', r'<h1 class="text-3xl font-bold mb-6">\1</h1>', html)
    html = re.sub(r'<h2>(.*?)</h2>', r'<h2 class="text-2xl font-semibold mb-4">\1</h2>', html)
    html = re.sub(r'<h3>(.*?)</h3>', r'<h3 class="text-xl font-semibold mt-6 mb-2">\1</h3>', html)
    
    # Add classes to paragraphs
    html = re.sub(r'<p>(.*?)</p>', r'<p class="mb-4">\1</p>', html)
    
    # Add classes to lists
    html = re.sub(r'<ul>', r'<ul class="list-disc pl-6 mb-4">', html)
    html = re.sub(r'<ol>', r'<ol class="list-decimal pl-6 mb-4">', html)
    html = re.sub(r'<li>(.*?)</li>', r'<li class="mb-2">\1</li>', html)
    
    return html

def create_main_html(html_content):
    sections = re.split(r'<h2', html_content)
    main_html = '<main class="w-full md:w-3/4 pr-0 md:pr-8" role="main">\n'
    
    # Process the first section (intro) separately
    intro = sections.pop(0)
    main_html += f'    <section class="bg-white shadow-md rounded-lg p-6 mb-8">\n{intro}\n    </section>\n'
    
    # Process the rest of the sections
    for section in sections:
        section = '<h2' + section  # Re-add the <h2 tag
        main_html += f'    <section class="bg-white shadow-md rounded-lg p-6 mb-8">\n{section}\n    </section>\n'
    
    main_html += '</main>'
    return main_html

fnames = ["Site/pt/data/analise-conclusoes", "Site/data/analysis-conclusions"]

for fname in fnames:

    # Read the Markdown file
    md_path = Path(f'{fname}.md')
    with md_path.open('r', encoding='utf-8') as md_file:
        md_content = md_file.read()

    # Convert Markdown to HTML
    html_content = md_to_html(md_content)

    # Create the main HTML structure
    new_main_html = create_main_html(html_content)

    # Read the existing HTML file
    html_path = Path(f'{fname.replace("data/","")}.html')
    with html_path.open('r', encoding='utf-8') as html_file:
        soup = BeautifulSoup(html_file, 'html.parser')

    # Find and replace the main tag
    main_tag = soup.find('main')
    if main_tag:
        new_main_tag = BeautifulSoup(new_main_html, 'html.parser').main
        main_tag.replace_with(new_main_tag)
    else:
        print("No <main> tag found in the HTML file.")
        exit(1)

    # Write the updated HTML back to the file
    with html_path.open('w', encoding='utf-8') as html_file:
        html_file.write(str(soup))

    print(f"The <main> content in {html_path} has been updated successfully.")