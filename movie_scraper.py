import requests
import json
import time

def get_movie_links(movie_name):
    # TMDB API ব্যবহার করে মুভির IMDB ID খুঁজে বের করা
    # (এটি একটি ডেমো এপিআই কী, আপনি TMDB থেকে ফ্রি কী নিতে পারেন)
    api_key = "844dba0bfd8f3a4f3799f6130ef9e335" 
    search_url = f"https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={movie_name}"
    
    links = []
    try:
        response = requests.get(search_url).json()
        if response['results']:
            movie_id = response['results'][0]['id']
            # বিভিন্ন ফ্রি মুভি সার্ভারের এমবেড লিঙ্ক জেনারেট করা
            links = [
                f"https://vidsrc.me/embed/movie?tmdb={movie_id}",
                f"https://2embed.org/embed/movie?tmdb={movie_id}",
                f"https://autoembed.to/movie/tmdb/{movie_id}"
            ]
    except Exception as e:
        print(f"Error for {movie_name}: {e}")
    
    return links

def main():
    movies = ["Deva", "Dhurandhar", "Avatar: The Way of Water"]
    results = []

    for name in movies:
        print(f"Generating links for: {name}")
        video_links = get_movie_links(name)
        
        results.append({
            "movie": name,
            "links": video_links,
            "total_found": len(video_links),
            "method": "API Generation",
            "updated": time.ctime()
        })

    with open('movies.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=4)
    print("Done! movies.json updated with API links.")

if __name__ == "__main__":
    main()
