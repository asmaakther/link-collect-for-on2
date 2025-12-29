import requests
import csv
import json
import os
import time
from bs4 import BeautifulSoup

# ১. গুগল শিট লিঙ্ক (না থাকলে খালি রাখুন)
SHEET_CSV_URL = "" 

# ২. আপনার টার্গেট ওয়েবসাইটগুলো
TARGET_SITES = [
    "https://www.movi.pk",
    "https://www.watch-movies.com.pk",
    "https://en.fmovies24-to.com/home"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
}

def get_movie_names():
    manual_list = [
      "Dhurandhar (2025) Hindi",
      "Avatar: Fire and Ash (2025) Hindi Dubbed",
      "Avatar (2025)",
      "Deva (2025) Hindi",
      "Cashero (2025) Hindi Dubbed Season 1 Complete",
      "The Woman in the Line 2025",
       "Man Finds Tape 2025"
    
    
    
    
    ] 
    sheet_list = []
    if SHEET_CSV_URL:
        try:
            response = requests.get(SHEET_CSV_URL, timeout=10)
            lines = response.text.splitlines()
            reader = csv.reader(lines)
            sheet_list = [row[0].strip() for row in reader if row]
        except:
            print("Google Sheet fetch failed, using manual list.")
    return list(set(manual_list + sheet_list))

def scrape_logic():
    MOVIE_NAMES = get_movie_names()
    
    # ৩. পুরাতন ডাটা লোড করা
    all_movies = []
    if os.path.exists('movies.json'):
        try:
            with open('movies.json', 'r', encoding='utf-8') as f:
                all_movies = json.load(f)
        except:
            all_movies = []

    # আগের মুভিগুলোর নাম ইনডেক্স করা
    existing_data = {m['name'].upper(): m for m in all_movies}
    new_found_count = 0

    for movie in MOVIE_NAMES:
        movie_upper = movie.upper()
        
        # যদি মুভিটি আগে থেকেই লিস্টে থাকে, তবে নতুন লিঙ্ক খোঁজার চেষ্টা করবে
        if movie_upper in existing_data:
            current_links = set(existing_data[movie_upper]['links'])
            print(f"Checking for new links for: {movie_upper}")
        else:
            current_links = set()
            print(f"Searching for new movie: {movie_upper}")

        new_links_added = False

        for site in TARGET_SITES:
            try:
                search_url = f"{site}/search?q={movie.lower()}"
                res = requests.get(search_url, headers=HEADERS, timeout=15)
                soup = BeautifulSoup(res.text, 'html.parser')
                
                # পোস্ট লিঙ্ক খুঁজে বের করা
                for a in soup.find_all('a', href=True):
                    if movie.lower() in a.text.lower() or movie.lower() in a['href'].lower():
                        post_res = requests.get(a['href'], headers=HEADERS, timeout=15)
                        post_soup = BeautifulSoup(post_res.text, 'html.parser')
                        
                        # ভিডিও সোর্স খোঁজা
                        for vid in post_soup.find_all(['source', 'a', 'video', 'iframe'], src=True):
                            src = vid.get('src') or vid.get('href')
                            if src and any(ext in src for ext in [".mp4", ".m3u8"]):
                                # ডুপ্লিকেট লিঙ্ক ফিল্টার (যদি লিঙ্কটি সেটে না থাকে তবেই যোগ হবে)
                                if src not in current_links:
                                    current_links.add(src)
                                    new_links_added = True
                                    print(f"Found unique link: {src}")
                time.sleep(1)
            except:
                continue

        # ডাটা আপডেট বা নতুন যোগ করা
        if new_links_added:
            if movie_upper in existing_data:
                existing_data[movie_upper]['links'] = list(current_links)
            else:
                existing_data[movie_upper] = {
                    "name": movie_upper,
                    "links": list(current_links)
                }
                new_found_count += 1

    # ৪. JSON ফাইলে সব ডাটা সেভ করা
    final_list = list(existing_data.values())
    with open('movies.json', 'w', encoding='utf-8') as f:
        json.dump(final_list, f, indent=4, ensure_ascii=False)
    
    print(f"\n--- কাজ শেষ! {new_found_count}টি নতুন মুভি/লিঙ্ক আপডেট হয়েছে। ---")

if __name__ == "__main__":
    scrape_logic()
