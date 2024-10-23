
from bs4 import BeautifulSoup
import requests
import os
import sys
import re
import itertools
from urllib.parse import urlparse, parse_qs


def next_page_urls(bsoup):
    next_links = bsoup.find_all("a", class_="next")
    hrefs = [link.get("href") for link in next_links]
    next_url = 'https://coomer.su/' + hrefs[0]
    return next_url

def save_files(bsoup):
    match_image = bsoup.find_all("a", class_='post__attachment-link')
    match_videos = bsoup.find_all("a", class_='fileThumb')
    print(match)
    hrefs = [link.get("href") for link in match_image]
    hrefs.extend(link.get("href") for link in match_videos)
    print(hrefs)
    for href in hrefs:
        parsed_url = urlparse(href)
        query_params = parse_qs(parsed_url.query)
        file_name = query_params.get('f', [''])[0]
        save_path = os.path.join(folder_name, file_name)
        response = requests.get(href, stream=True)
        if response.status_code == 200:
            with open(save_path, "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            print(f"File saved as {save_path}")

def posts(bsoup):
    pattern1 = "^/onlyfans/user/[a-zA-Z0-9]+/post/\d+"
    patter2 = "^/fansly/user/[a-zA-Z0-9]+/post/\d+"
    pattern = re.compile(f'{pattern1}|{pattern2}')
    # Find all 'a' tags with 'href' attributes matching the pattern
    matching_links = bsoup.find_all("a", href=pattern)

    # Extract the href values from the matching links
    hrefs = [ 'https://coomer.su'+link.get("href") for link in matching_links]

    return hrefs


url = sys.argv[1]
a = urlparse(url)

folder_name = os.path.basename(a.path)

if not os.path.exists(folder_name):
    os.makedirs(folder_name)

# Create a requests session
session = requests.Session()

# Set headers to mimic a browser request
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}


result = session.get(url, headers=headers)


soup = BeautifulSoup(result.content, "html.parser")

text = soup.get_text()

# Use a regular expression to find the number after "of "
match = re.search(r"Showing \d+ - \d+ of (\d+)", text)

if match:
    total_number = int(match.group(1))
    print(total_number)
else:
    print("The pattern was not found.")


page_links = []
page_links.append(url)
for i in range(0,int(total_number)//50 - 1):
    next_url = next_page_urls(soup)
    page_links.append(next_url)
    print(next_url)
    response = requests.get(next_url)
    try:
        if response.status_code == 200:
            # Parse the content of the new page
            soup = BeautifulSoup(response.content, "html.parser")
            next_url = next_page_urls(soup)
            response = requests.get(next_url)
            page_links.append(next_url)
    except IndexError:
        next_page_url = url

post_links = []
for url in set(page_links):
    result = session.get(url, headers=headers)
    soup = BeautifulSoup(result.content, "html.parser")
    links = posts(soup)
    post_links.append(links)

final_links = list(itertools.chain(*post_links))

for link in final_links:
    print(link)
    result = session.get(link, headers=headers)
    soup = BeautifulSoup(result.content, "html.parser")
    save_files(soup)






