import json
import time
import os
from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def scrape_movie():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--remote-debugging-port=9222')

    # Selenium-wire specific settings for GitHub Actions
    wire_options = {
        'request_storage_base_dir': '/tmp', # টেম্পোরারি ফাইল রাখার জায়গা
        'verify_ssl': False
    }

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options,
        seleniumwire_options=wire_options
    )

    target_url = "https://www.watch-movies.com.pk/deva-2024-hindi-movie-watch-online-free/"
    found_links = []

    try:
        print(f"Browsing: {target_url}")
        driver.get(target_url)
        time.sleep(20) # সাইটটি লোড হতে সময় নেয়

        for request in driver.requests:
            if request.response:
                url = request.url
                if ".m3u8" in url or ".mp4" in url:
                    if "googlevideo" not in url and "ads" not in url:
                        found_links.append(url)

        data = {
            "movie_name": "Deva",
            "source_url": target_url,
            "video_links": list(set(found_links)),
            "last_updated": time.ctime()
        }

        with open('movies.json', 'w') as f:
            json.dump(data, f, indent=4)
        
        print(f"Success! Found {len(found_links)} links.")

    except Exception as e:
        print(f"Error occurred: {e}")
        # এরর আসলে স্ক্রিপ্ট ফেইল করানোর জন্য exit(1) ব্যবহার করা হয়
        import sys
        sys.exit(1)
    finally:
        driver.quit()

if __name__ == "__main__":
    scrape_movie()
