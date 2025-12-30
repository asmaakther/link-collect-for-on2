import requests
import json
import os
import re
import time
from bs4 import BeautifulSoup

TARGET_SITES = [
    "https://www.watch-movies.com.pk",
    "https://www.movi.pk"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Referer": "https://www.google.com/"
}

def extract_links(html_text):
    """পেজের টেক্সট থেকে সব ধরণের ভিডিও এবং প্লেয়ার লিঙ্ক খুঁজে বের করে"""
    found = set()
    
    # ১. সরাসরি ভিডিও ফাইল খোঁজা (.m3u8, .mp4)
    video_patterns = [
        r'(https?://[^\s"\']+\.m3u8[^\s"\']*)',
        r'(https?://[^\s"\']+\.mp4[^\s"\']*)'
    ]
    for pattern in video_patterns:
        links = re.findall(pattern, html_text)
        for l in links:
            if "ads" not in l.lower():
                found.add(l.replace('\\', ''))

    # ২. থার্ড-পার্টি প্লেয়ার লিঙ্ক খোঁজা (এগুলো আপনার সাইটে এম্বেড করতে পারবেন)
    player_patterns = [
        r'https?://(?:www\.)?doodstream\.com/e/[a-z0-9]+',
        r'https?://(?:www\.)?streamwish\.(?:to|com)/e/[a-z0-9]+',
        r'https?://(?:www\.)?voe\.sx/e/[a-z0-9]+',
        r'https?://(?:www\.)?streamtape\.com/e/[a-z0-9]+',
        r'https?://(?:www\.)?fembed\.com/v/[a-z0-9]+'
    ]
    for pattern in player_patterns:
        links = re.findall(pattern, html_text, re.IGNORECASE)
        found.update(links)

    return list(found)

def main():
    MOVIE_NAMES = ["Deva", "Dhurandhar", "Avatar"] # আপনার মুভি লিস্ট
    results = []

    for movie in MOVIE_NAMES:
        print(f"Searching for: {movie}")
        movie_links = set()

        for site in TARGET_SITES:
            try:
                # সার্চ করা
                search_url = f"{site}/?s={movie.replace(' ', '+')}"
                response = requests.get(search_url, headers=HEADERS, timeout=15)
                soup = BeautifulSoup(response.text, 'html.parser')

                # প্রথম কয়েকটি পোস্টের লিঙ্ক নেওয়া
                links = soup.find_all('a', href=True)
                posts = []
                for a in links:
                    if movie.lower() in a.text.lower() or movie.lower() in a['href'].lower():
                        if site in a['href'] and a['href'] not in posts:
                            posts.append(a['href'])

                # প্রতিটি পোস্টের ভেতরে ঢুকা
                for post_url in posts[:2]: # প্রথম ২টা পোস্ট চেক করবে
                    print(f"  Checking: {post_url}")
                    p_res = requests.get(post_url, headers=HEADERS, timeout=15)
                    
                    # লিঙ্ক এক্সট্রাক্ট করা
                    links_in_post = extract_links(p_res.text)
                    movie_links.update(links_in_post)
                    
                    # আইফ্রেম চেক করা (অনেক সময় আইফ্রেমের ভেতরে লিঙ্ক থাকে)
                    p_soup = BeautifulSoup(p_res.text, 'html.parser')
                    for iframe in p_soup.find_all('iframe'):
                        src = iframe.get('src')
                        if src:
                            movie_links.add(src)
                
                time.sleep(1)
            except Exception as e:
                print(f"  Error on {site}: {e}")

        results.append({
            "movie": movie,
            "links": list(movie_links),
            "total_links": len(movie_links),
            "updated": time.ctime()
        })

    # JSON ফাইলে সেভ করা
    with open('movies.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=4, ensure_ascii=False)
    
    print("\nFinished! Results saved in movies.json")

if __name__ == "__main__":
    main()
