import cloudscraper
import random
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from rest_framework.decorators import api_view
from rest_framework.response import Response
from concurrent.futures import ThreadPoolExecutor, as_completed


PROXIES = [
    "http://dcznsktz:khvgikqdia1f@31.59.20.176:6754",
    "http://dcznsktz:khvgikqdia1f@23.95.150.145:6114",
    "http://dcznsktz:khvgikqdia1f@198.23.239.134:6540",
    "http://dcznsktz:khvgikqdia1f@45.38.107.97:6014",
    "http://dcznsktz:khvgikqdia1f@107.172.163.27:6543",
    "http://dcznsktz:khvgikqdia1f@198.105.121.200:6462",
    "http://dcznsktz:khvgikqdia1f@64.137.96.74:6641",
]


IGNORE_ANCHOR_TITLES = {
    "Naruto: Shippuden",
    "Solo Leveling Season 2: Arise from the Shadow",
    "Demon Slayer: Kimetsu no Yaiba Swordsmith Village Arc"
}


def get_random_proxy():
    proxy = random.choice(PROXIES)
    return {"http": proxy, "https": proxy}


# create scraper once (faster)
scraper = cloudscraper.create_scraper(
    browser={
        "browser": "chrome",
        "platform": "windows",
        "desktop": True
    }
)


headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36"
}


def fetch_episodes(anime_id, proxy):

    episode_data = []

    try:
        x = scraper.get(
            f"https://hianime.to/ajax/v2/episode/list/{anime_id}",
            headers=headers,
            proxies=proxy,
            timeout=15
        )

        y = x.json()
        x_text = y['html']

        episode_soup = BeautifulSoup(x_text, "html.parser")

        episodes_list = episode_soup.find_all(
            "a",
            attrs={"data-id": True, "data-number": True}
        )

        for episode in episodes_list:
            episode_data.append({
                "episode_id": episode.get("data-id"),
                "episode_number": episode.get("data-number"),
            })

    except Exception as e:
        print("Episode fetch failed:", e)

    return episode_data


@api_view(['POST'])
def anime_search(request):

    query = request.data.get('query')

    if not query:
        return Response({"error": "keyword required"}, status=400)

    query_for_url = quote_plus(query)
    url = f"https://hianime.to/search?keyword={query_for_url}"

    for attempt in range(5):

        proxy = get_random_proxy()
        print("Using Proxy:", proxy)

        try:

            r = scraper.get(
                url,
                headers=headers,
                proxies=proxy,
                timeout=15
            )

            print("Status:", r.status_code)

            if r.status_code != 200:
                continue

            soup = BeautifulSoup(r.text, "html.parser")

            posters = soup.find_all("img", class_="film-poster-img")

            Data = []
            tasks = []

            with ThreadPoolExecutor(max_workers=10) as executor:

                for poster in posters:

                    image = poster.get("data-src") or poster.get("src")
                    title = poster.get("alt")

                    desc = soup.find("a", title=title)

                    if not desc:

                        if title in IGNORE_ANCHOR_TITLES:
                            continue

                        print("Anchor not found for:", title)
                        continue

                    anime_id = desc.get("data-id")

                    if anime_id:
                        future = executor.submit(fetch_episodes, anime_id, proxy)
                        tasks.append((future, image, title))
                    else:
                        Data.append({
                            "image": image,
                            "title": title,
                            "episodes_data": []
                        })

                for future, image, title in tasks:

                    episode_data = future.result()

                    Data.append({
                        "image": image,
                        "title": title,
                        "episodes_data": episode_data
                    })

            return Response({
                "proxy_used": proxy["http"],
                "results": len(Data),
                "data": Data
            })

        except Exception as e:

            print("Proxy Failed:", proxy)
            print("Error:", str(e))
            continue

    return Response({"error": "All proxies failed"}, status=502)