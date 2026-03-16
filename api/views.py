import cloudscraper
import random
import re

from bs4 import BeautifulSoup
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


PROXIES = [
    "http://dcznsktz:khvgikqdia1f@31.59.20.176:6754",
    "http://dcznsktz:khvgikqdia1f@23.95.150.145:6114",
    "http://dcznsktz:khvgikqdia1f@198.23.239.134:6540",
    "http://dcznsktz:khvgikqdia1f@45.38.107.97:6014",
    "http://dcznsktz:khvgikqdia1f@107.172.163.27:6543",
    "http://dcznsktz:khvgikqdia1f@198.105.121.200:6462",
    "http://dcznsktz:khvgikqdia1f@64.137.96.74:6641",
]


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "X-Requested-With": "XMLHttpRequest",
}


scraper = cloudscraper.create_scraper(
    browser={
        "browser": "chrome",
        "platform": "windows",
        "mobile": False,
    }
)


def get_random_proxy():
    proxy = random.choice(PROXIES)
    return {"http": proxy, "https": proxy}


def fetch(url, params=None):
    """
    Reusable request function
    """
    try:
        response = scraper.get(
            url,
            headers=headers,
            params=params,
            proxies=get_random_proxy(),
            timeout=20
        )

        if response.status_code != 200:
            return None

        return response

    except Exception:
        return None


# SEARCH ANIME
@api_view(["POST"])
def anime_search(request):

    query = request.data.get("query")

    if not query:
        return Response(
            {"error": "query field required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    url = "https://9animetv.to/search"

    response = fetch(url, params={"keyword": query})

    if not response:
        return Response(
            {"error": "failed to fetch data"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    soup = BeautifulSoup(response.text, "lxml")

    container = soup.find_all("div", class_="flw-item item-qtip")

    if not container:
        return Response(
            {"results_found": 0, "results": []},
            status=status.HTTP_200_OK
        )

    results = []

    for item in container:

        anime_id = item.get("data-id")

        img = item.find("img")

        poster = img.get("data-src") if img else None
        title = img.get("alt") if img else None

        results.append({
            "anime_id": anime_id,
            "poster": poster,
            "title": title
        })

    return Response({
        "results_found": len(results),
        "results": results
    })


# EPISODE LIST
@api_view(["GET"])
def episode_detail(request, anime_id):

    url = f"https://9animetv.to/ajax/episode/list/{anime_id}"

    response = fetch(url)

    if not response:
        return Response(status=status.HTTP_404_NOT_FOUND)

    try:
        data = response.json()
    except:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    html = data.get("html")

    soup = BeautifulSoup(html, "lxml")

    episode_tags = soup.find_all("a", class_="item ep-item")

    episodes = []

    for ep in episode_tags:

        episodes.append({
            "episode_number": ep.get("data-number"),
            "episode_id": ep.get("data-id"),
        })

    return Response({
        "episode_count": len(episodes),
        "episodes": episodes
    })


# STREAM LINK
@api_view(["GET"])
def get_stream(request, episode_slug):

    numbers = re.findall(r'\d+', episode_slug)

    if not numbers:
        return Response(
            {"error": "invalid slug"},
            status=status.HTTP_400_BAD_REQUEST
        )

    ep_id = numbers[0]

    if episode_slug.endswith("english"):
        url = f"https://megaplay.buzz/stream/s-2/{ep_id}/dub"

    elif episode_slug.endswith("japanese"):
        url = f"https://megaplay.buzz/stream/s-2/{ep_id}/sub"

    else:
        return Response(
            {"error": "invalid format"},
            status=status.HTTP_400_BAD_REQUEST
        )

    return Response({
        "stream_url": url
    })