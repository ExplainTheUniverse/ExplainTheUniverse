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

def generate_post_summary(post_metadata, summary, image_url):
    """
    Generates the HTML block for a single post summary.
    """
    title = post_metadata.get('title', 'No Title')
    date = post_metadata.get('date', 'No Date')
    author = post_metadata.get('author', 'Unknown Author')
    slug = post_metadata.get('slug', title.lower().replace(' ', '-'))
    link = f"{slug}.html"

    # If an image URL is provided, add it as a background image
    background_style = f"background-image: url('{image_url}');" if image_url else ""

    html = f'''
    <div class="bg-black bg-opacity-50 rounded-lg shadow-md p-6 post-summary" style="{background_style}">
        <div class="overlay">
            <span class="text-sm text-gray-300">{date} • {author}</span>
            <h2 class="text-xl font-bold mt-2 mb-4">
                <a href="{link}" class="text-white hover:text-gray-200">
                    {title}
                </a>
            </h2>
            <p class="text-gray-200 mb-4">{summary}</p>
            <a href="{link}" class="text-white hover:text-gray-200">
                Read More →
            </a>
        </div>
    </div>
    '''
    return html

def process_markdown_files(markdown_dir='Site/content/blog', images_dir='Site/images/blog'):
    """
    Processes all markdown files to extract summaries and generate HTML blocks.
    """
    markdown_path = Path(markdown_dir)
    image_path = Path(images_dir)
    posts = []

    for md_file in markdown_path.glob('**/*.md'):
        # Skip files that start with 'draft-'
        if md_file.stem.startswith('draft-'):
            continue
            
        with open(md_file, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)
            content = post.content
            metadata = post.metadata

            # Ensure slug exists
            if 'slug' not in metadata:
                metadata['slug'] = md_file.stem

            slug = metadata['slug']
            # Assume image has the same name as markdown file with common image extensions
            possible_extensions = ['.jpg', '.jpeg', '.png', '.webp', '.gif']
            image_url = None
            for ext in possible_extensions:
                img_file = image_path / f"{slug}{ext}"
                if img_file.is_file():
                    image_url = f"../images/blog/{slug}{ext}"
                    break

            summary = extract_summary(content)
            posts.append({
                'metadata': metadata,
                'summary': summary,
                'image_url': image_url
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
    summaries_html = '\n'.join(generate_post_summary(post['metadata'], post['summary'], post.get('image_url')) for post in posts)

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