import requests
from bs4 import BeautifulSoup

url = "https://tepebasihem.meb.k12.tr/icerikler/icerikler/listele_69556_Haberler"
headers = {'User-Agent': 'Mozilla/5.0'}
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, 'html.parser')

for a in soup.find_all('a', href=True):
    href = a['href']
    title = a.get_text(strip=True)
    if 'icerik' in href.lower() or 'haber' in href.lower() or '.html' in href:
        print(f"LINK: {href} | TITLE: {title}")
