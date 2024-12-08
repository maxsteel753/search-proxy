# import requests
from bs4 import BeautifulSoup
# import json
import httpx
import time
import random
import string
from app.constants.ua import user_agents


def generate_random_string(length=10):
    characters = string.ascii_letters + string.digits  # Letters (uppercase and lowercase) + digits
    return ''.join(random.choice(characters) for _ in range(length))

def get_random_user_agent():
    user_agents_list = user_agents
    return random.choice(user_agents_list)

# def scrape_google_results(keyword, num_results=10, pages=1):
#     # Headers to mimic a browser user-agent
#     rand_string = generate_random_string(10)
#     proxy = "http://lumi-lumiproxysearch_area-US_session-"+rand_string+"_life-3:proxy123@us.lumiproxy.com:5888"
#     headers = {
#         "User-Agent": (
#             "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
#             "Chrome/89.0.4389.82 Safari/537.36"
#         ),
#         "Accept-Language": "en-US,en;q=0.9"
#     }
 
#     results = []
#     proxies = {
#         "http": proxy,
#         "https": proxy
#     } if proxy else None

#     for page in range(pages):
#         start = page * num_results  # Offset for pagination
#         query = keyword.replace(' ', '+')
#         url = f"https://www.google.com/search?q={query}&num={num_results}&start={start}"

#         try:
#             response = requests.get(url, headers=headers, proxies=proxies)

#             if response.status_code == 200:
#                 soup = BeautifulSoup(response.text, "html.parser")

#                 # Find search result elements
#                 for result in soup.select(".tF2Cxc"):
#                     print("search")
#                     title = result.select_one("h3").text if result.select_one("h3") else "No title"
#                     link = result.select_one(".yuRUbf a")["href"] if result.select_one(".yuRUbf a") else "No link"

#                     # Extract snippet (description text)
#                     snippet = ""
#                     snippet_div = result.select_one(".yXK7lf")  # Updated class for snippet text
#                     if snippet_div:
#                         snippet = snippet_div.text.strip()
#                     else:
#                         snippet = "No snippet available"

#                     results.append({
#                         "title": title,
#                         "link": link,
#                         "page": page + 1,
#                         "description": snippet,
#                         "keyword": keyword,
#                         "search_engine": "Google",
#                         "request_date": time.strftime("%Y-%m-%d %H:%M:%S")
#                     })
#             else:
#                 print(f"Failed to fetch results for page {page + 1}. HTTP Status Code: {response.status_code}")
#         except Exception as e:
#             print(f"An error occurred: {e}")

#     return results # Convert the list of results to a JSON-formatted string

async def scrape_google_results(keyword, num_results=10, pages=1, proxy=None):
    num_results = 10
    pages = 3
    rand_string = generate_random_string(10)
    proxy = "http://lumi-lumiproxysearch_area-US_session-"+rand_string+"_life-3:proxy123@us.lumiproxy.com:5888"
    # Headers to mimic a browser user-agent
    print(get_random_user_agent())
    headers = {
        "User-Agent": get_random_user_agent(),
        "Accept-Language": "en-US,en;q=0.9"
    }

    results = []
    proxies ={
            "http://": proxy,
            "https://": proxy
    } 
    
    async with httpx.AsyncClient(proxies=proxies) as client: 
        for page in range(pages):
            start = page * num_results  # Offset for pagination
            query = keyword.replace(' ', '+')
            url = f"https://www.google.com/search?q={query}&num={num_results}&start={start}"

            try:
                response = await client.get(url, headers=headers)

                if response.status_code == 200:                 
                    soup = BeautifulSoup(response.text, "html.parser")       
                    # Find search result elements
                    for result in soup.select(".tF2Cxc"):
                        
                        title = result.select_one("h3").text if result.select_one("h3") else "No title"
                        link = result.select_one(".yuRUbf a")["href"] if result.select_one(".yuRUbf a") else "No link"

                        # Extract snippet (description text)
                        snippet = ""
                        snippet_div = result.select_one(".yXK7lf")  # Updated class for snippet text
                        if snippet_div:
                            snippet = snippet_div.text.strip()
                        else:
                            snippet = "No snippet available"
                        results.append({
                            "title": title,
                            "link": link,
                            "page": page + 1,
                            "description": snippet,
                            "keyword": keyword,
                            "search_engine": "Google",
                            "request_date": time.strftime("%Y-%m-%d %H:%M:%S")
                        })
                else:
                    print(f"Failed to fetch results for page {page + 1}. HTTP Status Code: {response.status_code}")
            except Exception as e:
                print(f"An error occurred: {e}")
        return (results) 
