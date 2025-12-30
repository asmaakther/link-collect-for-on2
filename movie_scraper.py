from seleniumwire import webdriver # selenium-wire ব্যবহার করুন নেটওয়ার্ক ইন্টারসেপ্ট করার জন্য
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

def get_live_stream_link(url):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless') # ব্রাউজার উইন্ডো খুলবে না
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    print("ভিডিও লিঙ্ক খোঁজা হচ্ছে... একটু অপেক্ষা করুন।")
    driver.get(url)

    # ব্রাউজারের সব নেটওয়ার্ক রিকোয়েস্ট চেক করা
    for request in driver.requests:
        if request.response:
            # m3u8 বা mp4 ফাইল ফরম্যাট চেক করা
            if '.m3u8' in request.url or '.mp4' in request.url:
                print(f"লিঙ্ক পাওয়া গেছে: {request.url}")
                # আপনি চাইলে এখানে JSON এ সেভ করতে পারেন
    
    driver.quit()

# আপনার মুভি ইউআরএলটি এখানে দিন
get_live_stream_link("https://www.watch-movies.com.pk/deva-2024-hindi-movie-watch-online-free/")
