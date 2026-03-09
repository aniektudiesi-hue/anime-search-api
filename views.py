import requests
from bs4 import BeautifulSoup
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Using a session for better performance
session = requests.Session()

@api_view(["POST"])
def anime_search(request):
    # 1. Get keyword from POST body
    keyword = request.data.get("keyword", "").strip()
    if not keyword:
        return Response({"error": "keyword required"}, status=400)

    # 2. Use a robust User-Agent and Referer to prevent blocking
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Referer": "https://hianime.to/",
        "Accept-Language": "en-US,en;q=0.9",
    }

    try:
        # 3. Perform the request with a timeout
        url = "https://hianime.to/search"
        resp = session.get(url, params={"keyword": keyword}, headers=headers, timeout=10)
        resp.raise_for_status()

        # 4. Parse the HTML
        soup = BeautifulSoup(resp.text, "html.parser")
        results = []
        
        # The site uses 'flw-item' as the main container for each anime
        cards = soup.select(".flw-item")

        for card in cards:
            # Find the image and the link inside the film-poster div
            poster = card.select_one(".film-poster")
            if not poster:
                continue
                
            img = poster.find("img")
            link = poster.find("a")

            if not img or not link:
                continue

            # Sites often lazy-load images using data-src
            thumbnail = img.get("data-src") or img.get("src")
            href = link.get("href", "")

            # Extract the ID from the URL (e.g., /watch/naruto-677 -> naruto-677)
            episode_id = href.split("/")[-1] if href else None

            if thumbnail and episode_id:
                results.append({
                    "episode_id": episode_id,
                    "thumbnail": thumbnail
                })

            # Limit to top 20 results
            if len(results) >= 20:
                break

        return Response(results)

    except requests.exceptions.Timeout:
        return Response({"error": "Upstream site timed out"}, status=504)
    except requests.exceptions.RequestException as e:
        return Response({"error": str(e)}, status=502)
    except Exception as e:
        return Response({"error": "Internal server error during parsing"}, status=500)
