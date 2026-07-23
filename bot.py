import os
import requests
from bs4 import BeautifulSoup

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
URL = "https://tepebasihem.meb.k12.tr"
LAST_NEWS_FILE = "last_news.txt"

def send_telegram_message(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram credentials not found. Skipping message.")
        return
    
    send_text = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage?chat_id={TELEGRAM_CHAT_ID}&parse_mode=Markdown&text={message}'
    response = requests.get(send_text)
    return response.json()

def main():
    ajax_url = "https://tepebasihem.meb.k12.tr/tema/icerik_listele_ajax.php"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': 'https://tepebasihem.meb.k12.tr/icerikler/icerikler/listele_69556_Haberler'
    }
    data = {
        'kategori': '69556',
        'start': '0',
        'length': '1000'
    }
    
    try:
        response = requests.post(ajax_url, headers=headers, data=data, timeout=15)
        response.raise_for_status()
        json_data = response.json()
    except Exception as e:
        print(f"Error fetching the API: {e}")
        return

    items = json_data.get('data', [])
    if not items:
        print("Sayfada hic duyuru veya haber bulunamadi.")
        return
        
    # En yeni haberi bulmak için SIRAID değerine göre büyükten küçüğe sırala
    items.sort(key=lambda x: int(x.get('SIRAID', 0)), reverse=True)
    
    latest_item = items[0]
    latest_news_title = latest_item.get('BASLIK', '').replace('&quot;', '"')
    latest_news_link = latest_item.get('LINK', '')
    
    if latest_news_link and not latest_news_link.startswith('http'):
        latest_news_link = "https://tepebasihem.meb.k12.tr" + latest_news_link
        
    print(f"En son haber/duyuru bulundu: {latest_news_title}")
    
    # Kaydedilen son haberi oku
    last_news_saved = ""
    if os.path.exists(LAST_NEWS_FILE):
        with open(LAST_NEWS_FILE, 'r', encoding='utf-8') as f:
            last_news_saved = f.read().strip()
            
    if latest_news_title != last_news_saved:
        print("YENI BIR HABER/DUYURU VAR!")
        clean_link = latest_news_link.replace(" ", "%20")
        message = f"🚨 **YENİ KURS/HABER DUYURUSU** 🚨\n\n📌 *{latest_news_title}*\n\n🔗 [Detayları Gör]({clean_link})"
        send_telegram_message(message)
        
        # Dosyaya yeni haberi yaz
        with open(LAST_NEWS_FILE, 'w', encoding='utf-8') as f:
            f.write(latest_news_title)
    else:
        print("Yeni bir haber yok, son haber ayni.")

if __name__ == "__main__":
    main()
