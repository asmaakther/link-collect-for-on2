import requests
import csv
import json
import os
import time
from bs4 import BeautifulSoup

# ১. গুগল শিট লিঙ্ক (লিঙ্ক না থাকলে খালি "" রাখুন)
SHEET_CSV_URL = "" 

# ২. আপনার টার্গেট ওয়েবসাইটগুলো (আপনার নিজের ব্লগসহ আরও সাইট দিন)
TARGET_SITES = [
    "https://www.movi.pk",
    "https://www.watch-movies.com.pk",
    "https://en.fmovies24-to.com"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
}

def get_movie_names():
    """গুগল শিট এবং ম্যানুয়াল লিস্ট থেকে নাম সংগ্রহ করে"""
    manual_list = ["Dhurandhar (2025) Hindi",
      "Avatar: Fire and Ash (2025) Hindi Dubbed",
      "Avatar (2025)",
      "Deva (2025) Hindi",
      "Cashero (2025) Hindi Dubbed Season 1 Complete",
      "The Woman in the Line 2025",
       "Man Finds Tape 2025"] # এখানে আপনার মুভি লিস্ট দিন
    sheet_list = []
    if SHEET_CSV_URL:
        try:
            print("Reading Google Sheet...")
            response = requests.get(SHEET_CSV_URL, timeout=10)
            lines = response.text.splitlines()
            reader = csv.reader(lines)
            sheet_list = [row[0].strip() for row in reader if row]
        except:
            print("Google Sheet link not found. Using manual list.")
    
    return list(set(manual_list + sheet_list))

def scrape_logic():
    MOVIE_NAMES = get_movie_names()
    
    # ৩. পুরাতন ডাটা লোড করা (যাতে আগের মুভি ডিলিট না হয়)
    all_movies = []
    if os.path.exists('movies.json'):
        try:
            with open('movies.json', 'r', encoding='utf-8') as f:
                all_movies = json.load(f)
        except:
            all_movies = []

    # মুভির নাম অনুযায়ী ডাটা ম্যাপ তৈরি (সহজ আপডেটের জন্য)
    existing_data = {m['name'].upper(): m for m in all_movies}

    for movie in MOVIE_NAMES:
        movie_upper = movie.upper()
        
        # যদি মুভি আগে থেকেই থাকে, পুরাতন লিঙ্কগুলো সেটে রাখুন (ডুপ্লিকেট এড়াতে)
        if movie_upper in existing_data:
            current_links = set(existing_data[movie_upper]['links'])
            print(f"Checking for new links for: {movie_upper}")
        else:
            current_links = set()
            print(f"Searching new movie: {movie_upper}")

        new_links_found = False

        for site in TARGET_SITES:
            try:
                # ব্লগে মুভি সার্চ
                search_url = f"{site}/search?q={movie.lower()}"
                res = requests.get(search_url, headers=HEADERS, timeout=15)
                soup = BeautifulSoup(res.text, 'html.parser')
                
                # মুভির পোস্ট লিঙ্ক খোঁজা
                for a in soup.find_all('a', href=True):
                    if movie.lower() in a.text.lower() or movie.lower() in a['href'].lower():
                        post_url = a['href']
                        
                        # পোস্টের ভেতর থেকে ভিডিও লিঙ্ক খোঁজা
                        post_res = requests.get(post_url, headers=HEADERS, timeout=15)
                        post_soup = BeautifulSoup(post_res.text, 'html.parser')
                        
                        for vid in post_soup.find_all(['source', 'a', 'iframe', 'video', 'embed'], src=True):
                            src = vid.get('src') or vid.get('href')
                            
                            # mp4 বা m3u8 হলে ডুপ্লিকেট চেক করে যোগ করা
                            if src and any(ext in src.lower() for ext in [".mp4", ".m3u8"]):
                                if src not in current_links:
                                    current_links.add(src)
                                    new_links_found = True
                                    print(f"Found unique link: {src}")
                time.sleep(1)
            except:
                continue

        # যদি নতুন লিঙ্ক পাওয়া যায় বা মুভিটি নতুন হয়, তবে আপডেট করুন
        if new_links_found or movie_upper not in existing_data:
            if movie_upper not in existing_data:
                existing_data[movie_upper] = {"name": movie_upper, "links": []}
            
            existing_data[movie_upper]['links'] = list(current_links)

    # ৪. সব ডাটা (পুরাতন + নতুন) JSON এ সেভ করা
    final_output = list(existing_data.values())
    with open('movies.json', 'w', encoding='utf-8') as f:
        json.dump(final_output, f, indent=4, ensure_ascii=False)
    
    print("\n--- Scraping Finished! Check movies.json ---")

if __name__ == "__main__":
    scrape_logic()
