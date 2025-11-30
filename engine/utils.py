import requests
from bs4 import BeautifulSoup

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

        # Truncate Cleaned HTML -> Limit set to approx 12k tokens (~48k chars) to fit model context
        MAX_CHARS = 48000
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
        
        visible_text = soup.get_text(separator=' ', strip=True)

        if not cleaned_html and not visible_text:
            return None, None, None

        # RETURN TUPLE
        return url, cleaned_html, visible_text

    except (requests.RequestException, Exception):
        # RETURN 3 NONES (Safe Fallback)
        return None, None, None
