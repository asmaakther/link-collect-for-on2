import requests
import json
import os
import re
import time
from bs4 import BeautifulSoup

# ১. মুভি সাইট ও হেডার
TARGET_SITES = [
    "https://www.watch-movies.com.pk",
    "https://www.movi.pk"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
}

def get_direct_video_links(page_url):
    """পেজের ভেতর থেকে m3u8 বা ভিডিও সোর্স খুঁজে বের করার চেষ্টা করে"""
    links = set()
    try:
        response = requests.get(page_url, headers=HEADERS, timeout=15)
        # কন্টেন্টের ভেতর .m3u8 বা .mp4 আছে কিনা খোঁজা (Regex দিয়ে)
        m3u8_links = re.findall(r'(https?://[^\s"\']+\.m3u8[^\s"\']*)', response.text)
        mp4_links = re.findall(r'(https?://[^\s"\']+\.mp4[^\s"\']*)', response.text)
        
        for link in m3u8_links + mp4_links:
            if "google" not in link and "ads" not in link:
                links.add(link.replace('\\', '')) # ব্যাকস্ল্যাশ রিমুভ করা
                
        # যদি আইফ্রেম থাকে, তবে আইফ্রেমের সোর্স চেক করা
        soup = BeautifulSoup(response.text, 'html.parser')
        for iframe in soup.find_all('iframe'):
            src = iframe.get('src')
            if src:
                print(f"Found iframe source: {src}")
                # আপনি চাইলে এখানে আইফ্রেম সোর্সের ভেতরে গিয়েও আবার স্ক্র্যাপ করতে পারেন
                
    except Exception as e:
        print(f"Error fetching {page_url}: {e}")
    return list(links)

def main():
    MOVIE_NAMES = ["Deva (2025)", "Dhurandhar (2025)"]
    all_movies = []

    # পুরাতন ডাটা লোড করা
    if os.path.exists('movies.json'):
        with open('movies.json', 'r', encoding='utf-8') as f:
            all_movies = json.load(f)

    existing_data = {m['name'].upper(): m for m in all_movies}

    for movie in MOVIE_NAMES:
        movie_upper = movie.upper()
        print(f"Searching for: {movie_upper}")
        
        links_found = []
        for site in TARGET_SITES:
            try:
                # সার্চ রেজাল্ট পেজ
                search_url = f"{site}/?s={movie.replace(' ', '+')}"
                res = requests.get(search_url, headers=HEADERS, timeout=15)
                soup = BeautifulSoup(res.text, 'html.parser')
                
                # প্রথম ১-২টি মুভি পোস্টের লিঙ্ক নেওয়া
                for a in soup.find_all('a', href=True):
                    if movie.split(' ')[0].lower() in a.text.lower():
                        post_url = a['href']
                        print(f"Visiting Post: {post_url}")
                        video_links = get_direct_video_links(post_url)
                        links_found.extend(video_links)
                        break # শুধু প্রথম পোস্টটি চেক করবে
            except: continue

        existing_data[movie_upper] = {
            "name": movie_upper,
            "links": list(set(links_found)),
            "updated": time.ctime()
        }

    # JSON সেভ
    with open('movies.json', 'w', encoding='utf-8') as f:
        json.dump(list(existing_data.values()), f, indent=4, ensure_ascii=False)
    
    print("Done! Check movies.json")

if __name__ == "__main__":
    main()
