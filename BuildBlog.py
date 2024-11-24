import os
import re
from datetime import datetime
import frontmatter
import markdown
from pathlib import Path
import argparse
from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor
import xml.etree.ElementTree as etree

class TailwindTreeprocessor(Treeprocessor):
    """Add Tailwind CSS classes to HTML elements"""
    def run(self, root):
        self.root = root
        self.add_tailwind_classes(root)
        return root

    def add_tailwind_classes(self, element):
        # Add classes based on element type
        if element.tag == 'h2':
            element.set('class', 'text-2xl font-bold mb-4 mt-8')
        elif element.tag == 'h3':
            element.set('class', 'text-xl font-semibold mb-3')
        elif element.tag == 'h4':
            element.set('class', 'font-semibold mb-3')
        elif element.tag == 'p':
            element.set('class', 'mb-6')
        elif element.tag == 'ul':
            element.set('class', 'list-disc pl-6 mb-6 space-y-2 marker:text-gray-500')
            # Style list items within ul
            for li in element.findall('li'):
                li.set('class', 'pl-2')
        elif element.tag == 'ol':
            element.set('class', 'list-decimal pl-6 mb-6 space-y-2 marker:text-gray-500')
            # Style list items within ol
            for li in element.findall('li'):
                li.set('class', 'pl-2')
        elif element.tag == 'blockquote':
            ## border-l-4 border-blue-600 pl-4 mb-8 bg-gray-50 p-4
            element.set('class', 'border-l-4 border-blue-600 pl-4 mb-8 bg-gray-50 p-4 text-gray-700 italic')
            # Style paragraphs within blockquotes
            for p in element.findall('p'):
                # Remove the default paragraph margin and add blockquote-specific styling
                p.set('id', 'blockquote')
        # Process children
        for child in element:
            self.add_tailwind_classes(child)

class TailwindExtension(Extension):
    def extendMarkdown(self, md):
        md.treeprocessors.register(TailwindTreeprocessor(md), 'tailwind', 175)

class BlogPostConverter:
    def __init__(self, template_path='templates/post.html'):
        self.template_path = template_path
        
        # Read the template
        with open(template_path, 'r', encoding='utf-8') as f:
            self.template = f.read()

    def wrap_key_observations(self, html_content):
        """Wrap Key Observations section in gray containers"""
        # Find the Key Observations section and its content
        key_obs_pattern = r'(<h2[^>]*>Key Observations.*?</h2>)(.*?)(?=<h2|$)'
        
        def wrap_subsections(match):
            title, content = match.groups()
            # Wrap each subsection in gray container
            wrapped_content = re.sub(
                r'(<h3.*?</h3>)(.*?)(?=<h3|$)',
                r'<div class="bg-gray-50 p-6 rounded-lg mb-6">\1\2</div>',
                content,
                flags=re.DOTALL
            )
            return title + wrapped_content

        return re.sub(key_obs_pattern, wrap_subsections, html_content, flags=re.DOTALL)
            
    def read_markdown(self, md_path):
        """Read and parse markdown file with frontmatter"""
        post = frontmatter.load(md_path)
        return {
            'content': post.content,
            'metadata': post.metadata
        }
    
    def format_date(self, date_str):
        """Format date string to desired format"""
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        return date_obj.strftime('%B %d, %Y')
    
    def markdown_to_html(self, content):
        """Convert markdown to HTML with extensions and Tailwind classes"""
        md = markdown.Markdown(extensions=['extra', 'meta', TailwindExtension()])
        html = md.convert(content)
        # Add prose wrapper
        html = f'<div class="prose max-w-none">{html}</div>'
        # Wrap Key Observations subsections
        html = self.wrap_key_observations(html)
        return html
    
    def generate_category_links(self, categories):
        """Generate HTML for category tags"""
        category_template = '<a href="/blog/category/{slug}" class="px-3 py-1 bg-gray-100 rounded-full text-gray-700 hover:bg-gray-200">{name}</a>'
        return '\n'.join(
            category_template.format(
                slug=category.lower().replace(' ', '-'),
                name=category
            )
            for category in categories
        )

    def find_header_image(self, md_path):
        """Find corresponding header image for the markdown file"""
        md_path = Path(md_path)
        images_dir = Path('Site/images/blog')
        image_extensions = ['.webp', '.jpg', '.jpeg', '.png']
        base_name = md_path.stem  # e.g., 'alien-contact' from 'alien-contact.md'

        for ext in image_extensions:
            image_path = images_dir / f"{base_name}{ext}"
            if image_path.exists():
                return str(image_path.relative_to('Site'))
        return None

    def convert(self, md_path, output_path):
        """Convert markdown file to HTML and save"""
        # Read and parse markdown
        post_data = self.read_markdown(md_path)
        
        # Convert markdown content to HTML
        content_html = self.markdown_to_html(post_data['content'])
        
        # Format the date
        formatted_date = self.format_date(post_data['metadata']['date'])
        
        # Generate category tags
        category_links = self.generate_category_links(post_data['metadata']['categories'])
        
        # Find header image if exists
        header_image = self.find_header_image(md_path)
        header_image_html = f'''
        <div class="mb-6">
            <img src="../{header_image}" alt="Header Image for {post_data['metadata']['title']}" class="w-full h-auto rounded-lg"/>
        </div>
        ''' if header_image else '{{header_image}}'

        # Create the meta section with reading time
        reading_time = post_data['metadata'].get('readingTime', '')
        reading_time_html = f' • {reading_time}' if reading_time else ''
        
        meta_section = f'''
        <div class="mb-8">
            <span class="text-sm text-gray-500">{formatted_date} • {post_data['metadata']['author']}{reading_time_html}</span>
            <h2 class="text-3xl font-bold mt-2">{post_data['metadata']['title']}</h2>
        </div>
        {header_image_html}
        '''
        
        # Replace placeholders in template
        html = self.template
        replacements = {
            '{{title}}': post_data['metadata']['title'],
            '{{meta}}': meta_section,
            '{{content}}': content_html,
            '{{categories}}': category_links,
            '{{header_image}}': ''  # In case no image is present
        }
        
        for placeholder, value in replacements.items():
            html = html.replace(placeholder, value)
            
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Write the final HTML
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return output_path

def process_blog_posts(markdown_dir='content/blog', output_dir='public/blog', template_path='templates/post.html'):
    """Process all markdown files in a directory"""
    converter = BlogPostConverter(template_path)
    markdown_dir = Path(markdown_dir)
    output_dir = Path(output_dir)
    
    # Process each markdown file
    for md_file in markdown_dir.glob('**/*.md'):
        # Skip draft posts
        if md_file.stem.startswith('draft-'):
            print(f"Skipping draft post: {md_file}")
            continue
            
        # Determine output path
        relative_path = md_file.relative_to(markdown_dir)
        output_path = output_dir / relative_path.with_suffix('.html')
        
        # Convert the file
        try:
            converter.convert(str(md_file), str(output_path))
            print(f"Successfully converted {md_file} to {output_path}")
        except Exception as e:
            print(f"Error converting {md_file}: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description='Convert markdown blog posts to HTML')
    parser.add_argument('--markdown-dir', default='Site/content/blog', help='Directory containing markdown files')
    parser.add_argument('--output-dir', default='Site/blog', help='Directory for output HTML files')
    parser.add_argument('--template', default='Site/blog/_template.html', help='Path to HTML template file')
    
    args = parser.parse_args()
    
    process_blog_posts(args.markdown_dir, args.output_dir, args.template)

if __name__ == '__main__':
    main()
