import json
import time
from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def scrape_movie():
    # ব্রাউজার সেটিংস (গিটহাবের জন্য জরুরি)
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    # ড্রাইভার সেটআপ
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    target_url = "https://www.watch-movies.com.pk/deva-2024-hindi-movie-watch-online-free/"
    found_links = []

    try:
        print(f"Browsing: {target_url}")
        driver.get(target_url)
        
        # ভিডিও লোড হওয়ার জন্য ১৫ সেকেন্ড অপেক্ষা করুন
        time.sleep(15)

        # নেটওয়ার্ক ট্রাফিক থেকে m3u8 বা mp4 লিঙ্ক খোঁজা
        for request in driver.requests:
            if request.response:
                url = request.url
                if ".m3u8" in url or ".mp4" in url:
                    if "googlevideo" not in url: # ফালতু গুগল অ্যাড বাদ দিতে
                        found_links.append(url)

        # রেজাল্ট JSON এ সেভ করা
        data = {
            "movie_name": "Deva",
            "source_url": target_url,
            "video_links": list(set(found_links)), # ডুপ্লিকেট লিঙ্ক বাদ দিতে
            "last_updated": time.ctime()
        }

        with open('movies.json', 'w') as f:
            json.dump(data, f, indent=4)
        
        print("Success! JSON file updated.")

    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    scrape_movie()
