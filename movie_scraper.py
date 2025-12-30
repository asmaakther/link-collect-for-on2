import requests
import re
import urllib.parse
import json
import time

def get_movie_package(movie_name):
    # TMDB API Key
    api_key = "844dba0bfd8f3a4f3799f6130ef9e335" 
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    # ১. TMDB থেকে মুভির তথ্য ও আইডি সংগ্রহ
    tmdb_url = f"https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={movie_name}"
    try:
        movie_data = requests.get(tmdb_url).json()
        if not movie_data['results']:
            print(f"No TMDB data found for: {movie_name}")
            return None
        
        movie = movie_data['results'][0]
        m_id = movie['id']
        title = movie['title']
        desc = movie.get('overview', 'Watch this full movie online for free in high quality.')
        img = f"https://image.tmdb.org/t/p/w780{movie.get('backdrop_path')}"
    except Exception as e:
        print(f"TMDB Error: {e}")
        return None

    # ২. OK.ru থেকে ভিডিও লিঙ্ক সার্চ করা
    ok_link = ""
    search_q = f"{movie_name} full movie site:ok.ru/video"
    google_url = f"https://www.google.com/search?q={urllib.parse.quote(search_q)}"
    
    try:
        search_res = requests.get(google_url, headers=headers)
        ok_ids = re.findall(r'ok\.ru/video/(\d+)', search_res.text)
        if ok_ids:
            ok_link = f"https://ok.ru/videoembed/{ok_ids[0]}"
    except:
        ok_link = ""

    # ৩. সার্ভার লিস্ট তৈরি (যদি OK.ru থাকে তবে সেটি আগে থাকবে)
    # ডিফল্ট সার্ভার (VidSrc TO)
    primary_server = f"https://vidsrc.to/embed/movie/{m_id}"
    ok_button_html = ""
    
    if ok_link:
        # যদি OK.ru পাওয়া যায়, তবে সেটিকে মেইন প্লেয়ার হিসেবে সেট করা
        default_player = ok_link
        ok_button_html = f'<button onclick="document.getElementById(\'main_player\').src=\'{ok_link}\'" style="background:#f39c12; color:#fff; padding:12px 20px; border:none; border-radius:5px; cursor:pointer; font-weight:bold;">Server 1 (OK.ru - NO ADS)</button>'
    else:
        default_player = primary_server

    # ৪. ব্লগস্পটের জন্য ফাইনাল HTML
    html_template = f"""
<div style="display:none;"><img src="{img}" /></div>

<div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; max-width: 850px; margin: 20px auto; background: #fff; border: 1px solid #eee; border-radius: 12px; overflow: hidden; box-shadow: 0 5px 15px rgba(0,0,0,0.1);">
    
    <img src="{img}" style="width: 100%; height: auto; display: block;" alt="{title}" />
    
    <div style="padding: 20px;">
        <h1 style="color: #222; font-size: 26px; margin: 0 0 10px 0; text-align: center;">{title} Dubbed in Hindi Watch Full Movie Free</h1>
        
        <div style="background: #f9f9f9; padding: 15px; border-radius: 8px; margin-bottom: 20px; border-left: 5px solid #e74c3c;">
            <p style="margin: 0; color: #555; font-size: 15px; line-height: 1.6;"><b>Storyline:</b> {desc}</p>
        </div>

        <h3 style="text-align: center; color: #333; margin-bottom: 15px;">🎥 Select Server to Watch Online</h3>

        <div style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; border-radius: 10px; background: #000; box-shadow: 0 4px 12px rgba(0,0,0,0.3);">
            <iframe id="main_player" src="{default_player}" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: none;" allowfullscreen></iframe>
        </div>

        <div style="margin-top: 20px; display: flex; flex-wrap: wrap; justify-content: center; gap: 10px;">
            {ok_button_html}
            <button onclick="document.getElementById('main_player').src='https://vidsrc.to/embed/movie/{m_id}'" style="background:#e74c3c; color:#fff; padding:12px 20px; border:none; border-radius:5px; cursor:pointer; font-weight:bold;">Server 2 (Fast)</button>
            <button onclick="document.getElementById('main_player').src='https://embed.smashystream.com/playere.php?tmdb={m_id}'" style="background:#3498db; color:#fff; padding:12px 20px; border:none; border-radius:5px; cursor:pointer; font-weight:bold;">Server 3 (HD)</button>
            <button onclick="document.getElementById('main_player').src='https://vidsrc.me/embed/movie?tmdb={m_id}'" style="background:#2ecc71; color:#fff; padding:12px 20px; border:none; border-radius:5px; cursor:pointer; font-weight:bold;">Server 4 (Backup)</button>
        </div>
        
        <p style="text-align:center; font-size: 12px; color: #888; margin-top: 15px;">Note: If Server 1 doesn't work, please try other servers. Ads may appear on some servers.</p>
    </div>
</div>
"""
    return {"title": f"{title} (2025) Hindi Dubbed Full Movie Watch Online Free", "html": html_template}

# --- ব্যবহার করার নিয়ম ---
# মুভির নামগুলো এখানে লিস্ট আকারে দিন
movies_to_post = ["Avatar: The Way of Water", "Pushpa 2: The Rule", "Deva (2025)"]

print("--- GENERATING BLOG POSTS ---")
for movie_name in movies_to_post:
    result = get_movie_package(movie_name)
    if result:
        print("\n" + "="*50)
        print(f"POST TITLE: {result['title']}")
        print("="*50)
        print(result['html'])
        print("="*50)
        time.sleep(2) # Google/TMDB ব্লক এড়াতে বিরতি
