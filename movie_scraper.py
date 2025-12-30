import requests
import re
import urllib.parse
import json
import time

def get_movie_complete_data(movie_name):
    api_key = "844dba0bfd8f3a4f3799f6130ef9e335" # TMDB API Key
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    
    # ১. TMDB থেকে ডাটা, আইডি এবং পোস্টার সংগ্রহ
    tmdb_url = f"https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={movie_name}"
    try:
        res = requests.get(tmdb_url).json()
        if not res['results']:
            return None
        
        movie = res['results'][0]
        m_id = movie['id']
        title = movie['title']
        
        # পোস্টার এবং ব্যাকড্রপ (আপনার সাইটের জন্য ব্যাকড্রপ বেশি ভালো হবে)
        poster = f"https://image.tmdb.org/t/p/w500{movie.get('poster_path')}" if movie.get('poster_path') else ""
        backdrop = f"https://image.tmdb.org/t/p/w780{movie.get('backdrop_path')}" if movie.get('backdrop_path') else ""
        
        # ২. OK.ru লিঙ্ক খোঁজার চেষ্টা
        ok_link = ""
        search_q = f"{movie_name} full movie site:ok.ru/video"
        google_url = f"https://www.google.com/search?q={urllib.parse.quote(search_q)}"
        
        try:
            search_res = requests.get(google_url, headers=headers)
            # রেগুলার এক্সপ্রেশন দিয়ে ভিডিও আইডি খোঁজা
            ok_ids = re.findall(r'ok\.ru/video/(\d+)', search_res.text)
            if ok_ids:
                ok_link = f"https://ok.ru/videoembed/{ok_ids[0]}"
        except:
            ok_link = "Not Found"

        # ৩. ডাটা স্ট্রাকচার তৈরি
        return {
            "movie": title,
            "tmdb_id": m_id,
            "poster_link": poster,
            "backdrop_link": backdrop,
            "ok_ru_link": ok_link,
            "embed_links": [
                f"https://vidsrc.to/embed/movie/{m_id}",
                f"https://embed.smashystream.com/playere.php?tmdb={m_id}",
                f"https://vidsrc.me/embed/movie?tmdb={m_id}"
            ],
            "updated": time.ctime()
        }
    except Exception as e:
        print(f"Error: {e}")
        return None

# মুভি লিস্ট রান করা
movies = ["Deva", "Dhurandhar", "Avatar: The Way of Water"]
final_results = []

for m in movies:
    print(f"Processing: {m}...")
    data = get_movie_complete_data(m)
    if data:
        final_results.append(data)
    time.sleep(2) # গুগল ব্লক এড়াতে গ্যাপ

# JSON ফাইলে সেভ করা
with open('movies_updated.json', 'w', encoding='utf-8') as f:
    json.dump(final_results, f, indent=4)

print("\n✅ Success! movies_updated.json চেক করুন।")
