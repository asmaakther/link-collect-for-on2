import json
import os
import time
import sys
from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def scrape_logic():
    # ১. মুভি লিস্ট
    MOVIE_NAMES = ["Deva (2025) Hindi", "Dhurandhar (2025) Hindi"]
    TARGET_SITES = ["https://www.watch-movies.com.pk", "https://www.movi.pk"]
    
    # ২. পুরাতন ডাটা লোড
    all_movies = []
    if os.path.exists('movies.json'):
        try:
            with open('movies.json', 'r', encoding='utf-8') as f:
                all_movies = json.load(f)
        except: pass
    
    existing_data = {m['name'].upper(): m for m in all_movies}

    # ৩. ব্রাউজার কনফিগারেশন (গিটহাবের জন্য ক্রিটিক্যাল)
    chrome_options = Options()
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--remote-debugging-port=9222')

    wire_options = {
        'request_storage_base_dir': '/tmp',
        'verify_ssl': False
    }

    driver = None
    try:
        print("Starting WebDriver...")
        # লাইন ৩৩ এর সমাধান এখানে: সঠিক ড্রাইভার সার্ভিস সেটআপ
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options, seleniumwire_options=wire_options)
        driver.set_page_load_timeout(60)

        for movie in MOVIE_NAMES:
            movie_upper = movie.upper()
            print(f"--- Searching: {movie_upper} ---")
            current_links = set(existing_data.get(movie_upper, {}).get('links', []))

            for site in TARGET_SITES:
                try:
                    search_url = f"{site}/?s={movie.replace(' ', '+')}"
                    driver.get(search_url)
                    time.sleep(15) # মুভি সাইট লোড হতে সময় নেয়

                    # নেটওয়ার্ক ট্রাফিক থেকে ডিরেক্ট লিঙ্ক বের করা
                    for request in driver.requests:
                        if request.response:
                            url = request.url
                            if any(ext in url.lower() for ext in [".m3u8", ".mp4"]):
                                if "ads" not in url.lower() and "google" not in url.lower():
                                    current_links.add(url)
                                    print(f"Match Found: {url[:50]}...")
                    
                    # রিকোয়েস্ট ক্লিয়ার করা (মেমোরি সেভ করতে)
                    del driver.requests
                except Exception as e:
                    print(f"Site Error: {e}")
                    continue

            existing_data[movie_upper] = {"name": movie_upper, "links": list(current_links)}

        # ৪. JSON সেভ করা
        with open('movies.json', 'w', encoding='utf-8') as f:
            json.dump(list(existing_data.values()), f, indent=4, ensure_ascii=False)
        
        print("Scraping Finished Successfully!")

    except Exception as e:
        print(f"!!! CRITICAL ERROR AT LINE 33 or below: {e}")
        sys.exit(1)
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    scrape_logic()
