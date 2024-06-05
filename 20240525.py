import requests
from newsapi import NewsApiClient
import openai
import os
import re

# Initialize NewsApiClient
newsapi = NewsApiClient(api_key='409d870d05424180b32bc04f872584a4')  # Replace with your News API key
# Get OpenAI API key from environment variable
openai.api_key = os.getenv('OPENAI_API_KEY')

def generate_summary(text):
    """Generate a summary using OpenAI API."""
    try:
        response = openai.Completion.create(
            model="gpt-3.5-turbo-instruct",
            prompt=f"Summarize this article:\n\n{text}",
            max_tokens=100,
            temperature=0.3,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )
        summary = response.choices[0].text.strip()
        return summary
    except Exception as e:
        print(f"Error generating summary: {e}")
        return "Summary not available"

def sanitize_prompt(prompt):
    """Sanitize the prompt to avoid triggering safety systems."""
    prohibited_keywords = ["violence", "hate", "disaster", "war", "death", "crime"]
    for keyword in prohibited_keywords:
        prompt = prompt.replace(keyword, "")
    return prompt

def generate_image(prompt):
    """Generate an image using OpenAI DALL·E and return its URL."""
    sanitized_prompt = sanitize_prompt(prompt)
    try:
        response = openai.Image.create(
            prompt=sanitized_prompt,
            n=1,
            size="256x256"  # Ensure the size is 256x256
        )
        image_url = response['data'][0]['url']
        return image_url
    except Exception as e:
        print(f"Error generating image: {e}")
        return 'placeholder_image_url.png'  # Fallback to a placeholder image if generation fails

def fetch_full_content(url):
    """Fetch the full content of the article from the URL."""
    try:
        content_response = requests.get(url)
        if content_response.status_code == 200:
            full_content = content_response.text
            # Strip HTML tags if necessary
            clean_content = re.sub('<[^<]+?>', '', full_content)
            return clean_content
        else:
            return "Full content not available"
    except Exception as e:
        print(f"Error fetching full content: {e}")
        return "Full content not available"

# Get the top five headlines from BBC News
top_headlines = newsapi.get_top_headlines(
    sources='bbc-news',
    language='en',
    page_size=5
)

# Prepare HTML structure
html_content = '''<html>
<head>
<title>News Summary</title>
<style>
body { font-family: Arial, sans-serif; margin: 20px; background-color: #f4f4f4; color: #333; }
header { background-color: #bb1919; color: white; padding: 10px 20px; text-align: center; }
.header-title { font-size: 2em; margin: 0; }
.news-container { display: flex; flex-direction: column; gap: 20px; margin: 20px 0; }
.news-card { background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); overflow: hidden; display: flex; flex-direction: row; align-items: flex-start; gap: 20px; padding: 20px; }
.news-card-content { width: 66%; }
.news-card-image { width: 33%; text-align: center; }
.news-card h2 { margin: 0 0 10px; font-size: 1.5em; }
.news-card p { margin: 0 0 10px; line-height: 1.6; }
.news-card a { color: #bb1919; text-decoration: none; font-weight: bold; }
.news-card img { width: 256px; height: 256px; border-radius: 8px; }
.footer { text-align: center; margin: 20px 0; color: #666; }
</style>
</head>
<body>
<header>
  <div class="header-title">BBC News Summary</div>
</header>
<div class="news-container">
</div>
<footer class="footer">
  <p>News summaries provided by BBC News and OpenAI</p>
</footer>
</body>
</html>'''

news_cards = ""
if 'articles' in top_headlines and top_headlines['articles']:
    articles = top_headlines['articles']
    
    for article in articles:
        title = article['title']
        author = article.get('author', 'BBC News')
        url = article['url']
        content = article.get('content', 'No content available')

        # Check for ellipses indicating truncated content
        if '...' in content:
            # Fetch the full content from the article URL
            full_content = fetch_full_content(url)
        else:
            full_content = content

        summary = generate_summary(full_content)
        image_url = generate_image(summary)  # Generate image based on the summary
        if image_url is None:
            image_url = 'placeholder_image_url.png'  # Fallback to a placeholder image if generation fails
        
        news_cards += f'''<div class="news-card">
<div class="news-card-content">
<h2>{title}</h2>
<p>By {author}</p>
<p>{summary}</p>
<p><a href="{url}" target="_blank">{url}</a></p>
</div>
<div class="news-card-image">
<img src="{image_url}" alt="News Image">
</div>
</div>'''

html_content = html_content.replace('<div class="news-container">', f'<div class="news-container">{news_cards}')

with open('news_summary_with_images.html', 'w', encoding='utf-8') as file:
    file.write(html_content)

print("News summary with images has been saved to 'news_summary_with_images.html'")