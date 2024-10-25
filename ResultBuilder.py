import re
import markdown
from bs4 import BeautifulSoup
import os
import glob

def read_file(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return file.read()

def write_file(filename, content):
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(content)

def extract_content(markdown_content):
    ai_name = re.search(r'AI_NAME: (.+)', markdown_content).group(1)
    exec_date = re.search(r'EXEC_DATE: (.+)', markdown_content).group(1)
    
    prompts = []
    current_prompt = {}
    lines = markdown_content.split('\n')
    capturing_text = False
    capturing_response = False
    
    for line in lines:
        if line.startswith('PROMPT_TITLE:'):
            if current_prompt:
                prompts.append(current_prompt)
            current_prompt = {'title': line.split(':', 1)[1].strip()}
            capturing_text = False
            capturing_response = False
        elif line.startswith('PROMPT_TEXT:'):
            current_prompt['text'] = ''
            capturing_text = True
            capturing_response = False
        elif line.startswith('PROMPT_RESP:'):
            current_prompt['response'] = ''
            capturing_text = False
            capturing_response = True
        elif line.startswith('PROMPT_SEP'):
            prompts.append(current_prompt)
            current_prompt = {}
            capturing_text = False
            capturing_response = False
        elif capturing_text:
            current_prompt['text'] += line + '\n'
        elif capturing_response:
            current_prompt['response'] += line + '\n'
    
    if current_prompt:
        prompts.append(current_prompt)
    
    # Clean extra whitespace
    for prompt in prompts:
        if 'text' in prompt:
            prompt['text'] = prompt['text'].strip()
        if 'response' in prompt:
            prompt['response'] = prompt['response'].strip()
    
    return ai_name, exec_date, prompts

def apply_template(template, ai_name, exec_date, prompts, en=False):
    soup = BeautifulSoup(template, 'html.parser')
    
    # Update AI name
    str_placeholder = soup.find(string=re.compile(r'\[AI_NAME\]'))
    if str_placeholder:
        str_placeholder.replace_with(ai_name)
    
    # Update exec date
    str_placeholder = soup.find(string=re.compile(r'\[EXEC_DATE\]'))
    if str_placeholder:
        str_placeholder.replace_with(exec_date)
    
    # Find the container for prompts
    prompt_container = soup.find('div', class_='space-y-4')
    
    # Clear existing prompts
    prompt_container.clear()
    
    # Add new prompts
    for index, prompt in enumerate(prompts, start=1):
        prompt_div = soup.new_tag('div', **{'class': 'bg-white shadow-md rounded-lg overflow-hidden mb-4'})
        
        header = soup.new_tag('div', **{'class': 'prompt-header bg-gray-200 px-6 py-4 cursor-pointer flex justify-between items-center'})
        header_text = soup.new_tag('span')
        header_text.string = f"Prompt {index}: {prompt['title']}"
        header.append(header_text)
        
        chevron = soup.new_tag('svg', **{'class': 'chevron-icon w-5 h-5', 'fill': 'currentColor', 'viewBox': '0 0 20 20'})
        path = soup.new_tag('path', **{'fill-rule': 'evenodd', 'd': 'M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z', 'clip-rule': 'evenodd'})
        chevron.append(path)
        header.append(chevron)
        
        content = soup.new_tag('div', **{'class': 'prompt-content px-6 py-4'})
        
        prompt_text = soup.new_tag('h4', **{'class': 'font-bold mb-2 text-blue-500'})
        prompt_text.string = 'Prompt:'
        content.append(prompt_text)
        
        prompt_p = soup.new_tag('p', **{'class': 'mb-4'})
        prompt_p.string = prompt['text']
        content.append(prompt_p)
        
        response_text = soup.new_tag('h4', **{'class': 'font-bold mb-2 text-blue-500'})
        response_text.string = 'Resposta:' if not en else "Response:"
        content.append(response_text)
        
        # Convert Markdown to HTML
        response_html = markdown.markdown(prompt['response'])
        response_div = soup.new_tag('div', **{'class': 'markdown-content'})
        response_div.append(BeautifulSoup(response_html, 'html.parser'))
        content.append(response_div)
        
        prompt_div.append(header)
        prompt_div.append(content)
        prompt_container.append(prompt_div)
    
    return str(soup)

# Main execution
template_content = read_file('Site/pt/resultados/_template.html')

# Process all markdown files in the Site/pt/data/resultados directory, excluding the template
markdown_files = glob.glob('Site/pt/data/resultados/*.md')
markdown_files = [f for f in markdown_files if not f.endswith('_template.md')]

for markdown_file in markdown_files:
    print(f"Processing {markdown_file}...")
    markdown_content = read_file(markdown_file)
    ai_name, exec_date, prompts = extract_content(markdown_content)
    result = apply_template(template_content, ai_name, exec_date, prompts)
    
    # Generate output HTML filename
    output_filename = os.path.basename(markdown_file).replace('.md', '.html')
    output_path = os.path.join('Site/pt/resultados', output_filename)
    
    write_file(output_path, result)
    print(f"Generated {output_path}")
    

# Main execution Site
template_content = read_file('Site/results/_template.html')

# Process all markdown files in the Site/data/results directory, excluding the template
markdown_files = glob.glob('Site/data/results/*.md')
markdown_files = [f for f in markdown_files if not f.endswith('_template.md')]

for markdown_file in markdown_files:
    print(f"Processing EN {markdown_file}...")
    markdown_content = read_file(markdown_file)
    ai_name, exec_date, prompts = extract_content(markdown_content)
    result = apply_template(template_content, ai_name, exec_date, prompts, True)
    
    # Generate output HTML filename
    output_filename = os.path.basename(markdown_file).replace('.md', '.html')
    output_path = os.path.join('Site/results', output_filename)
    
    write_file(output_path, result)
    print(f"Generated EN {output_path}")

