import requests
import json
import os
import re
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin

TARGET_SITES = [
    "https://www.watch-movies.com.pk",
    "https://www.movi.pk"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Referer": "https://www.google.com/"
}

def clean_link(link):
    """লিঙ্ক থেকে অপ্রয়োজনীয় ক্যারেক্টার রিমুভ করে এবং পূর্ণাঙ্গ ইউআরএল বানায়"""
    if not link or "data:image" in link or "base64" in link:
        return None
    link = link.replace('\\', '').strip()
    if link.startswith('//'):
        link = 'https:' + link
    return link

def extract_from_script(html_text):
    """জাভাস্ক্রিপ্ট কোডের ভেতর লুকিয়ে থাকা m3u8 বা mp4 লিঙ্ক খোঁজে"""
    found = set()
    patterns = [
        r'https?://[^\s"\']+\.m3u8[^\s"\']*',
        r'https?://[^\s"\']+\.mp4[^\s"\']*',
        r'https?://(?:www\.)?(?:doodstream|dood|streamwish|voe|streamtape|fembed)\.[a-z0-9]+/e/[a-zA-Z0-9]+'
    ]
    for pattern in patterns:
        matches = re.findall(pattern, html_text, re.IGNORECASE)
        for m in matches:
            if "ads" not in m.lower():
                found.add(m)
    return found

def main():
    # মুভির নাম (আপনি চাইলে আরও মুভি যোগ করতে পারেন)
    MOVIE_NAMES = ["Deva", "Dhurandhar", "Avatar"] 
    final_results = []

    for movie in MOVIE_NAMES:
        print(f"\n🔍 Searching for: {movie}")
        movie_links = set()

        for site in TARGET_SITES:
            try:
                search_url = f"{site}/?s={movie.replace(' ', '+')}"
                response = requests.get(search_url, headers=HEADERS, timeout=15)
                soup = BeautifulSoup(response.text, 'html.parser')

                # সার্চ রেজাল্ট থেকে পোস্টের লিঙ্কগুলো বের করা
                post_links = []
                for a in soup.find_all('a', href=True):
                    if movie.lower() in a.text.lower() or movie.lower() in a['href'].lower():
                        full_post_url = urljoin(site, a['href'])
                        if full_post_url not in post_links:
                            post_links.append(full_post_url)

                # প্রতিটি মুভি পোস্টে ঢুকে গভীর অনুসন্ধান
                for post_url in post_links[:2]: # প্রথম ২টা ইউনিক পোস্ট চেক করবে
                    print(f"  📂 Checking Post: {post_url}")
                    p_res = requests.get(post_url, headers=HEADERS, timeout=15)
                    
                    # ১. সরাসরি স্ক্রিপ্ট থেকে লিঙ্ক খোঁজা
                    script_links = extract_from_script(p_res.text)
                    movie_links.update(script_links)
                    
                    # ২. আইফ্রেম ও এমবেড ট্যাগ থেকে সোর্স খোঁজা
                    p_soup = BeautifulSoup(p_res.text, 'html.parser')
                    for tag in p_soup.find_all(['iframe', 'embed', 'source', 'video']):
                        # সব ধরণের সোর্স অ্যাট্রিবিউট চেক করা (Lazy loading bypass)
                        potential_src = (
                            tag.get('src') or 
                            tag.get('data-src') or 
                            tag.get('data-lazy-src') or 
                            tag.get('data-litesrc') or
                            tag.get('data-original')
                        )
                        
                        valid_link = clean_link(potential_src)
                        if valid_link:
                            # যদি লিঙ্কটি সরাসরি মুভি সার্ভার হয়
                            if any(x in valid_link for x in ['.m3u8', '.mp4', 'dood', 'streamwish', 'voe', 'player']):
                                movie_links.add(valid_link)
                                print(f"    ✅ Found: {valid_link[:60]}...")
                
                time.sleep(1)
            except Exception as e:
                print(f"  ❌ Error on {site}: {e}")

        final_results.append({
            "movie": movie,
            "links": list(movie_links),
            "total_links_found": len(movie_links),
            "last_updated": time.ctime()
        })

    # JSON সেভ করা
    with open('movies.json', 'w', encoding='utf-8') as f:
        json.dump(final_results, f, indent=4, ensure_ascii=False)
    
    print("\n✅ Scraping Completed! Results saved in movies.json")

if __name__ == "__main__":
    main()
