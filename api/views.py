import cloudscraper
import random

from bs4 import BeautifulSoup
from urllib.parse import quote

import re
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

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
    "Accept": "application/json, text/javascript, */*; q=0.01",  # Added Accept header for AJAX calls
    "X-Requested-With": "XMLHttpRequest"  # Added X-Requested-With header for AJAX calls
}

# GLOBAL SCRAPER
scraper = cloudscraper.create_scraper(
    browser={
        "browser": "chrome",
        "platform": "windows",
        "mobile": False,
    }
)


def get_random_proxy():
    proxy = random.choice(PROXIES)
    return proxy

@api_view(["POST"])
def anime_search(request):

    results = []
    query = request.data.get("query")
    encoded = quote(query)
    url = f"https://9animetv.to/search?keyword={encoded}"
    x = scraper.get(url, headers=headers, proxies={'https': get_random_proxy()})
    y = x.text
    soup = BeautifulSoup(y, "lxml")
    container = soup.find_all("div", class_="flw-item item-qtip")
    if not container:
        return Response(status=status.HTTP_404_NOT_FOUND)
    for item in container:
        anime_id = item.get("data-id")
        poster = item.find("img").get("data-src")
        title = item.find("img").get("alt")
        results.append({
            "anime_id": anime_id,
            "poster": poster,
            "title": title
        })
    return Response({"results_found":len(results),"results":results}, status=status.HTTP_200_OK)
@api_view(["GET"])
def episode_detail(request,anime_id):
    episode_data = []

    url = f"https://9animetv.to/ajax/episode/list/{anime_id}"
    x = scraper.get(url, headers=headers, proxies={'https': get_random_proxy()}).json()
    if not x:
        return Response(status=status.HTTP_404_NOT_FOUND)
    y = x["html"]
    ep_soup = BeautifulSoup(y, "lxml")
    episode_class = ep_soup.find_all("a",class_="item ep-item")
    if not episode_class:
        return Response(status=status.HTTP_404_NOT_FOUND)
    for episodes in episode_class:
        episode_id = episodes.get("data-id")
        episode_number = episodes.get("data-number")
        episode_data.append({
            "episode_number": episode_number,
            "episode_id": episode_id,
        })
    return Response({"episode_data":episode_data}, status=status.HTTP_200_OK)
@api_view(["GET"])
def get_stream(request,episode_slug):
    url = "Invalid Slug Request Should be in a valid format"
    numbers = re.findall(r'\d+', episode_slug)[0]
    if episode_slug == f"{numbers}-english":
        url = f"https://megaplay.buzz/stream/s-2/{numbers}/dub"
    if episode_slug == f"{numbers}-japanese":
        url = f"https://megaplay.buzz/stream/s-2/{numbers}/sub"
    return Response(url)