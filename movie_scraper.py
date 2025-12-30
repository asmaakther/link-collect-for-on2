import json
import time
import sys
from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def scrape_movie():
    options = Options()
    options.add_argument('--headless=new') # নতুন হেডলেস মোড
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')

    # GitHub Actions-এ selenium-wire এর জন্য কনফিগারেশন
    wire_options = {
        'request_storage_base_dir': '/tmp',
        'verify_ssl': False
    }

    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(
            service=service,
            options=options,
            seleniumwire_options=wire_options
        )

        target_url = "https://www.watch-movies.com.pk/deva-2024-hindi-movie-watch-online-free/"
        print(f"Browsing: {target_url}")
        
        driver.get(target_url)
        time.sleep(25) # সাইটটি বেশ ভারী, তাই সময় বাড়ানো হলো

        found_links = []
        for request in driver.requests:
            if request.response:
                url = request.url
                if ".m3u8" in url or ".mp4" in url:
                    if "ads" not in url.lower() and "google" not in url.lower():
                        found_links.append(url)

        data = {
            "movie_name": "Deva",
            "video_links": list(set(found_links)),
            "last_updated": time.ctime()
        }

        with open('movies.json', 'w') as f:
            json.dump(data, f, indent=4)
        
        print(f"Done! Found {len(found_links)} links.")

    except Exception as e:
        print(f"Error Detail: {e}")
        sys.exit(1) # এরর হলে গিটহাবকে জানানো
    finally:
        if 'driver' in locals():
            driver.quit()

if __name__ == "__main__":
    scrape_movie()
