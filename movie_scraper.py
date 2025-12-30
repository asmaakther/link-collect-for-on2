import requests
import json
import re
import time
from bs4 import BeautifulSoup

# আমরা সরাসরি মুভি পেজের ভেতরের সোর্স কোড স্ক্যান করব
TARGET_SITES = [
    "https://www.watch-movies.com.pk",
    "https://www.movi.pk"
]

# একদম রিয়াল ব্রাউজার হেডার
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1"
}

def deep_search_links(html):
    """এটি জাভাস্ক্রিপ্ট কোড এবং হিডেন ট্যাগের ভেতর থেকে প্লেয়ার লিঙ্ক খুঁজে বের করবে"""
    found = set()
    # ১. জনপ্রিয় ভিডিও হোস্টিং প্যাটার্ন
    patterns = [
        r'https?://(?:dood|doodstream|ds2play)\.[a-z0-9]+/e/[a-zA-Z0-9]+',
        r'https?://(?:streamwish|awish|strwish)\.[a-z0-9]+/e/[a-zA-Z0-9]+',
        r'https?://(?:voe|voe-sx)\.[a-z0-9]+/e/[a-zA-Z0-9]+',
        r'https?://(?:streamtape|stape)\.[a-z0-9]+/e/[a-zA-Z0-9]+',
        r'https?://(?:gdriveplayer|gembed)\.[a-z0-9]+/embed\?[^"\']+',
        r'https?://[^\s"\']+\.m3u8[^\s"\']*'
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, html, re.IGNORECASE)
        for m in matches:
            found.add(m.replace('\\', ''))
            
    return found

def main():
    MOVIE_NAMES = ["Deva", "Dhurandhar", "Avatar"]
    final_data = []

    for movie in MOVIE_NAMES:
        print(f"--- 🔎 Searching: {movie} ---")
        movie_links = set()

        for site in TARGET_SITES:
            try:
                # সরাসরি সার্চ কুয়েরি পাঠানো
                search_url = f"{site}/?s={movie.replace(' ', '+')}"
                session = requests.Session() # সেশন ব্যবহার করা হচ্ছে যাতে কুকি কাজ করে
                r = session.get(search_url, headers=HEADERS, timeout=20)
                
                soup = BeautifulSoup(r.text, 'html.parser')
                
                # মুভি পোস্টের লিঙ্কগুলো বের করা
                for a in soup.find_all('a', href=True):
                    # মুভির নাম যদি লিঙ্কে বা টেক্সটে থাকে
                    if movie.lower() in a.text.lower() or movie.lower() in a['href'].lower():
                        post_url = a['href']
                        print(f"   📂 Opening Post: {post_url}")
                        
                        # পোস্টের ভেতর গিয়ে লিঙ্ক খোঁজা
                        p_res = session.get(post_url, headers=HEADERS, timeout=20)
                        
                        # হিডেন লিঙ্ক খোঁজা
                        links = deep_search_links(p_res.text)
                        movie_links.update(links)
                        
                        # যদি আইফ্রেম থাকে
                        p_soup = BeautifulSoup(p_res.text, 'html.parser')
                        for iframe in p_soup.find_all('iframe'):
                            src = iframe.get('src') or iframe.get('data-src')
                            if src and "http" in src:
                                if any(x in src for x in ['dood', 'wish', 'voe', 'player']):
                                    movie_links.add(src)

                time.sleep(2) # সার্ভারকে সময় দিন
            except Exception as e:
                print(f"   ❌ Error: {e}")

        final_data.append({
            "movie": movie,
            "links": list(movie_links),
            "total_found": len(movie_links),
            "last_updated": time.ctime()
        })

    with open('movies.json', 'w', encoding='utf-8') as f:
        json.dump(final_data, f, indent=4, ensure_ascii=False)
    
    print("\n✅ Done! Check movies.json")

if __name__ == "__main__":
    main()
