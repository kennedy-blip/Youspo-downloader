import requests
from bs4 import BeautifulSoup

def get_spotify_artwork_no_api(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
    }
    try:
        # Standardize URL (remove tracking query params)
        clean_url = url.split('?')[0]
        response = requests.get(clean_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Metadata check
        img_tag = soup.find("meta", property="og:image")
        title_tag = soup.find("meta", property="og:title")
        
        if img_tag:
            return img_tag["content"], title_tag["content"] if title_tag else "Spotify Art"
    except Exception as e:
        print(f"Spotify Scraper Error: {e}")
    return None, None