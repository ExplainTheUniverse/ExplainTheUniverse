import os
import re
from datetime import datetime
import frontmatter
from pathlib import Path

def extract_summary(content, max_length=200):
    """
    Extracts a summary from the markdown content.
    Here, we use the first 2 paragraphs as the summary.
    """
    paragraphs = re.split(r'\n\s*\n', content)
    summary = ' '.join(paragraphs[:2])
    summary = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', summary)  # Remove markdown links
    summary = re.sub(r'[*_>`~]', '', summary)  # Remove other markdown syntax
    if len(summary) > max_length:
        summary = summary[:max_length].rsplit(' ', 1)[0] + '...'
    return summary

def generate_post_summary(post_metadata, summary):
    """
    Generates the HTML block for a single post summary.
    """
    title = post_metadata.get('title', 'No Title')
    date = post_metadata.get('date', 'No Date')
    author = post_metadata.get('author', 'Unknown Author')
    categories = post_metadata.get('categories', [])
    slug = post_metadata.get('slug', title.lower().replace(' ', '-'))
    link = f"{slug}.html"

    category_links = ' '.join(
        f'<a href="/blog/category/{cat.lower().replace(" ", "-")}" class="px-3 py-1 bg-gray-100 rounded-full text-gray-700 hover:bg-gray-200">{cat}</a>'
        for cat in categories
    )

    html = f'''
    <div class="bg-white rounded-lg shadow-md p-6">
        <span class="text-sm text-gray-500">{date} • {author}</span>
        <h2 class="text-xl font-bold mt-2 mb-4">
            <a href="{link}" class="text-blue-600 hover:text-blue-800">
                {title}
            </a>
        </h2>
        <p class="text-gray-700 mb-4">{summary}</p>
        <div class="flex flex-wrap gap-2 mb-4">
            {category_links}
        </div>
        <a href="{link}" class="text-blue-600 hover:text-blue-800">
            Read More →
        </a>
    </div>
    '''
    return html

def process_markdown_files(markdown_dir='Site/content/blog'):
    """
    Processes all markdown files to extract summaries and generate HTML blocks.
    """
    markdown_path = Path(markdown_dir)
    posts = []

    for md_file in markdown_path.glob('**/*.md'):
        with open(md_file, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)
            content = post.content
            metadata = post.metadata

            # Ensure slug exists
            if 'slug' not in metadata:
                metadata['slug'] = md_file.stem

            summary = extract_summary(content)
            posts.append({
                'metadata': metadata,
                'summary': summary
            })

    # Sort posts by date descending
    try:
        posts.sort(key=lambda x: datetime.strptime(x['metadata']['date'], '%Y-%m-%d'), reverse=True)
    except Exception as e:
        print(f"Error sorting posts by date: {e}")
        # Optionally, handle different date formats or missing dates

    return posts

def update_posts_html(posts, template_path='Site/blog/_template-posts.html', output_html_path='Site/blog/_posts.html'):
    """
    Updates the _posts.html file with the generated post summaries.
    """
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()
    except FileNotFoundError:
        print(f"Template file {template_path} not found.")
        return

    # Generate HTML for all posts
    summaries_html = '\n'.join(generate_post_summary(post['metadata'], post['summary']) for post in posts)

    # Replace the placeholder with the generated summaries
    if '{{post_summaries}}' in template:
        updated_html = template.replace('{{post_summaries}}', summaries_html)
    else:
        print("Placeholder '{{post_summaries}}' not found in the template.")
        return

    # Write back to _posts.html
    with open(output_html_path, 'w', encoding='utf-8') as f:
        f.write(updated_html)

    print(f"Updated {output_html_path} with {len(posts)} post summaries.")

def main():
    posts = process_markdown_files()
    update_posts_html(posts)

if __name__ == '__main__':
    main() 