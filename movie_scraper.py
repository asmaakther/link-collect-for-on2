import json
import os
import time
import sys
from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

TARGET_SITES = [
    "https://www.watch-movies.com.pk",
    "https://www.movi.pk"
]

def scrape_logic():
    # ম্যানুয়াল মুভি লিস্ট
    MOVIE_NAMES = ["Deva (2025) Hindi", "Dhurandhar (2025) Hindi"]
    
    # পুরাতন ডাটা লোড
    all_movies = []
    if os.path.exists('movies.json'):
        with open('movies.json', 'r', encoding='utf-8') as f:
            all_movies = json.load(f)
    
    existing_data = {m['name'].upper(): m for m in all_movies}

    # ব্রাউজার সেটআপ
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    wire_options = {'request_storage_base_dir': '/tmp', 'verify_ssl': False}
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options,
        seleniumwire_options=wire_options
    )

    for movie in MOVIE_NAMES:
        movie_upper = movie.upper()
        print(f"Searching for: {movie_upper}")
        current_links = set(existing_data.get(movie_upper, {}).get('links', []))

        for site in TARGET_SITES:
            try:
                # ১. সার্চ পেজে যাওয়া
                search_url = f"{site}/?s={movie.replace(' ', '+')}"
                driver.get(search_url)
                time.sleep(5)

                # ২. প্রথম মুভি পোস্টের লিঙ্ক খুঁজে বের করা (সাধারণত এ ট্যাগ থাকে)
                # আমরা ধরে নিচ্ছি সার্চ রেজাল্টের প্রথম লিঙ্কে মুভি আছে
                page_source = driver.page_source
                if movie.split(' ')[0].lower() in page_source.lower():
                    # এখানে ড্রাউভারকে সরাসরি মুভি পেজে নিয়ে যাওয়ার লজিক
                    # উদাহরণস্বরূপ সরাসরি পেজে ভিজিট করছি
                    target_movie_page = driver.current_url 
                    
                    print(f"Extracting links from network traffic...")
                    # নেটওয়ার্ক ট্রাফিক চেক করা
                    for request in driver.requests:
                        if request.response:
                            url = request.url
                            if any(ext in url for ext in [".m3u8", ".mp4"]):
                                if "google" not in url and "ads" not in url:
                                    current_links.add(url)
                                    print(f"Link Found: {url}")
            except Exception as e:
                print(f"Error on {site}: {e}")
                continue

        existing_data[movie_upper] = {"name": movie_upper, "links": list(current_links)}

    # JSON সেভ করা
    with open('movies.json', 'w', encoding='utf-8') as f:
        json.dump(list(existing_data.values()), f, indent=4, ensure_ascii=False)
    
    driver.quit()
    print("Scraping Finished!")

if __name__ == "__main__":
    scrape_logic()
