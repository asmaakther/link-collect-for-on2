import requests
import json

def generate_blogspot_posts(movie_names):
    api_key = "844dba0bfd8f3a4f3799f6130ef9e335"
    final_output = []

    for name in movie_names:
        search_url = f"https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={name}"
        try:
            res = requests.get(search_url).json()
            if res['results']:
                movie = res['results'][0]
                m_id = movie['id']
                title = movie['title']
                overview = movie.get('overview', 'Watch this amazing full movie online for free in high quality.')
                img = f"https://image.tmdb.org/t/p/w780{movie.get('backdrop_path')}"
                
                # সম্পূর্ণ রেসপন্সিভ এবং মোবাইল ফ্রেন্ডলি HTML
                html_code = f"""
<img src="{img}" style="display:none;" />

<div style="max-width: 800px; margin: auto; background: #f9f9f9; padding: 15px; border-radius: 10px; font-family: sans-serif; border: 1px solid #ddd;">
    <img src="{img}" style="width: 100%; border-radius: 8px; margin-bottom: 15px;" />
    
    <h1 style="font-size: 22px; color: #e74c3c; text-align: center;">{title} Dubbed in Hindi Watch Full Movie Free</h1>
    
    <div style="background: #fff; padding: 15px; border-radius: 5px; margin-bottom: 20px; color: #555; border-left: 4px solid #e74c3c;">
        <b>Storyline:</b> {overview}
    </div>

    <h3 style="text-align: center;">⬇️ WATCH ONLINE BELOW ⬇️</h3>

    <div style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; border-radius: 8px; background: #000;">
        <iframe id="player_{m_id}" src="https://vidsrc.to/embed/movie/{m_id}" 
                style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: none;" allowfullscreen></iframe>
    </div>

    <div style="margin-top: 15px; display: flex; flex-wrap: wrap; justify-content: center; gap: 10px;">
        <button onclick="document.getElementById('player_{m_id}').src='https://vidsrc.to/embed/movie/{m_id}'" style="padding: 10px 15px; background: #e74c3c; color: #fff; border: none; border-radius: 4px; cursor: pointer;">Server 1</button>
        <button onclick="document.getElementById('player_{m_id}').src='https://embed.smashystream.com/playere.php?tmdb={m_id}'" style="padding: 10px 15px; background: #3498db; color: #fff; border: none; border-radius: 4px; cursor: pointer;">Server 2</button>
        <button onclick="document.getElementById('player_{m_id}').src='https://vidsrc.me/embed/movie?tmdb={m_id}'" style="padding: 10px 15px; background: #2ecc71; color: #fff; border: none; border-radius: 4px; cursor: pointer;">Server 3</button>
    </div>
</div>
"""
                final_output.append({"title": f"{title} Hindi Dubbed Full Movie", "content": html_code})
        except:
            continue
    return final_output

# আপনি যে মুভিগুলো চাচ্ছেন তার নাম এখানে দিন
movies = ["Deva", "Avatar: The Way of Water", "Pushpa 2: The Rule"]
all_posts = generate_blogspot_posts(movies)

for post in all_posts:
    print(f"TITLE: {post['title']}")
    print(post['content'])
    print("-" * 50)
