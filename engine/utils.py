import yaml
import requests
import io
from bs4 import BeautifulSoup
from pathlib import Path
from markitdown import MarkItDown

def load_config(file_path: str = None) -> dict:
    file_path = Path(__file__).parent / "config.yaml"
    with open(file_path, "r") as f:
        return yaml.safe_load(f)

def process_website_data(url: str) -> tuple:
    try:
        # Fetch URL -> Raw HTML
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        # Parse with BeautifulSoup (Once)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Clean Tags (Style, Noscript)
        for tag in soup(['style', 'noscript']):
            tag.decompose()
        
        # Remove external stylesheet links
        for tag in soup.find_all('link', rel='stylesheet'):
            tag.decompose()

        cleaned_html = str(soup)

        # Truncate Cleaned HTML -> Limit set to approx 5k tokens (~20k chars) to fit Groq TPM limits
        MAX_CHARS = 20000
        if len(cleaned_html) > MAX_CHARS:
            truncated_raw = cleaned_html[:MAX_CHARS]
            last_tag_index = truncated_raw.rfind('>')
            
            if last_tag_index != -1:
                cleaned_html = truncated_raw[:last_tag_index + 1] + "\n"
            else:
                cleaned_html = truncated_raw + "\n"

        # Extract Text from Soup
        for tag in soup(['script']):
            tag.decompose()
        
        binary_stream = io.BytesIO(soup.encode('utf-8'))
        md = MarkItDown()
        result = md.convert_stream(binary_stream, file_extension=".html")
        visible_text = result.text_content

        # Truncate visible text -> Limit to approx 5k tokens (~20k chars) for TPM limits
        MAX_TEXT_CHARS = 20000
        if len(visible_text) > MAX_TEXT_CHARS:
            visible_text = visible_text[:MAX_TEXT_CHARS] + "\n[Content truncated...]"

        if not cleaned_html and not visible_text:
            return None, None, None

        # RETURN TUPLE
        return url, cleaned_html, visible_text

    except (requests.RequestException, Exception):
        # RETURN 3 NONES (Safe Fallback)
        return None, None, None
