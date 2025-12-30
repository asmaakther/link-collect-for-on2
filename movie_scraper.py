import json
import time
import sys
import os
from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def scrape_movie():
    print("Initializing Chrome in Headless Mode...")
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

    # Selenium-wire options for GitHub Actions environment
    wire_options = {
        'request_storage_base_dir': '/tmp',
        'verify_ssl': False
    }

    driver = None
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(
            service=service,
            options=options,
            seleniumwire_options=wire_options
        )

        target_url = "https://www.watch-movies.com.pk/deva-2024-hindi-movie-watch-online-free/"
        print(f"Browsing: {target_url}")
        
        # টাইমআউট সেট করা
        driver.set_page_load_timeout(60)
        driver.get(target_url)
        
        print("Waiting for video elements to load (30 seconds)...")
        time.sleep(30) # মুভি সাইটগুলো লোড হতে অনেক সময় নেয়

        found_links = []
        print("Searching network traffic for .m3u8 or .mp4...")
        
        for request in driver.requests:
            if request.response:
                url = request.url
                # ভিডিও ফাইল ফরম্যাট চেক
                if any(ext in url for ext in [".m3u8", ".mp4", "/playlist.m3u8"]):
                    if "ads" not in url.lower() and "google" not in url.lower():
                        found_links.append(url)

        # ইউনিক লিঙ্কগুলো ফিল্টার করা
        unique_links = list(set(found_links))
        
        data = {
            "movie_name": "Deva",
            "video_links": unique_links,
            "count": len(unique_links),
            "last_updated": time.ctime()
        }

        with open('movies.json', 'w') as f:
            json.dump(data, f, indent=4)
        
        if unique_links:
            print(f"Success! Found {len(unique_links)} links.")
        else:
            print("Warning: No video links found. Site might be blocking the bot.")

    except Exception as e:
        print(f"!!! CRITICAL ERROR: {str(e)}")
        sys.exit(1)
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    scrape_movie()
