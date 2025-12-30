import requests
import json
import os
import re
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin

TARGET_SITES = [
    "https://www.watch-movies.com.pk",
     "https://moviebox.ph",
     "https://movies123.pk",
    "https://www.movi.pk"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def get_links_from_html(html_content, base_url):
    """HTML কন্টেন্ট থেকে সব ধরণের m3u8, mp4 এবং ভিডিও সোর্স খুঁজে বের করে"""
    links = set()
    
    # ১. Regex ব্যবহার করে সরাসরি লিঙ্ক খোঁজা (Script এর ভেতর থেকে)
    regex_patterns = [
        r'(https?://[^\s"\']+\.m3u8[^\s"\']*)',
        r'(https?://[^\s"\']+\.mp4[^\s"\']*)',
        r'file:\s*["\'](https?://[^"\']+)["\']'
    ]
    
    for pattern in regex_patterns:
        found = re.findall(pattern, html_content)
        for link in found:
            clean_link = link.replace('\\', '')
            if "google" not in clean_link and "ads" not in clean_link:
                links.add(clean_link)
    
    # ২. BeautifulSoup দিয়ে iframe এবং source ট্যাগ খোঁজা
    soup = BeautifulSoup(html_content, 'html.parser')
    for tag in soup.find_all(['iframe', 'source', 'video', 'embed']):
        src = tag.get('src') or tag.get('data-src')
        if src:
            full_url = urljoin(base_url, src)
            if any(ext in full_url.lower() for ext in [".m3u8", ".mp4"]):
                links.add(full_url)
            # যদি থার্ড পার্টি প্লেয়ারের লিঙ্ক পায় (যেমন DoodStream, Streamwish)
            elif any(provider in full_url for provider in ["dood", "streamwish", "voe", "fembed"]):
                links.add(full_url)
                
    return list(links)

def main():
    # আপনি যে মুভিগুলো খুঁজছেন
    MOVIE_NAMES = ["Deva", "Bahubali","Undercover High School Hindi","Dhurandhar", "Avatar"]
    all_movies_data = []

    for movie in MOVIE_NAMES:
        print(f"Searching for Movie: {movie}")
        movie_links = set()
        
        for site in TARGET_SITES:
            try:
                # সার্চ পেজ ভিজিট
                search_url = f"{site}/?s={movie.replace(' ', '+')}"
                res = requests.get(search_url, headers=HEADERS, timeout=15)
                soup = BeautifulSoup(res.text, 'html.parser')
                
                # প্রথম ৩টি পোস্টের লিঙ্ক খুঁজে বের করা
                post_count = 0
                for a in soup.find_all('a', href=True):
                    if movie.lower() in a.text.lower() and post_count < 3:
                        post_url = a['href']
                        print(f"   - Checking Post: {post_url}")
                        
                        post_res = requests.get(post_url, headers=HEADERS, timeout=15)
                        links = get_links_from_html(post_res.text, post_url)
                        movie_links.update(links)
                        post_count += 1
                        time.sleep(1)
            except Exception as e:
                print(f"   ! Error on {site}: {e}")
                
        all_movies_data.append({
            "name": movie,
            "links": list(movie_links),
            "updated_at": time.ctime()
        })

    # JSON ফাইলে সেভ করা
    with open('movies.json', 'w', encoding='utf-8') as f:
        json.dump(all_movies_data, f, indent=4, ensure_ascii=False)
    
    print("\nScraping Finished. Results saved to movies.json")

if __name__ == "__main__":
    main()
