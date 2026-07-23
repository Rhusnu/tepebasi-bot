import os
import requests
from bs4 import BeautifulSoup

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
URL = "https://tepebasihem.meb.k12.tr/icerikler/icerikler/listele_69556_Haberler"
LAST_NEWS_FILE = "last_news.txt"

def send_telegram_message(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram credentials not found. Skipping message.")
        return
    
    send_text = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage?chat_id={TELEGRAM_CHAT_ID}&parse_mode=Markdown&text={message}'
    response = requests.get(send_text)
    return response.json()

def main():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    try:
        response = requests.get(URL, headers=headers, timeout=15)
        response.raise_for_status()
    except Exception as e:
        print(f"Error fetching the URL: {e}")
        return

    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Tüm linkleri al
    news_items = soup.find_all('a')
    latest_news_title = None
    latest_news_link = None
    
    for item in news_items:
        href = item.get('href', '')
        title = item.get_text(strip=True)
        # Haber veya duyuru linki mi diye kontrol et
        if href and title and ('/icerikler/' in href and href.endswith('.html')):
            if len(title) > 5: 
                # Tarih kısmı genelde başlığın sonuna bitişik yazılıyor (örn: KURSU17-07-2026)
                # Orijinal başlığı almak için temizleyebiliriz ama olduğu gibi kullanmak da güvenli
                latest_news_title = title
                latest_news_link = href
                if not latest_news_link.startswith('http'):
                    latest_news_link = "https://tepebasihem.meb.k12.tr" + latest_news_link
                break
                
    if not latest_news_title:
        print("Sayfada hic duyuru veya haber bulunamadi.")
        return
        
    print(f"En son haber/duyuru bulundu: {latest_news_title}")
    
    # Kaydedilen son haberi oku
    last_news_saved = ""
    if os.path.exists(LAST_NEWS_FILE):
        with open(LAST_NEWS_FILE, 'r', encoding='utf-8') as f:
            last_news_saved = f.read().strip()
            
    if latest_news_title != last_news_saved:
        print("YENI BIR HABER/DUYURU VAR!")
        # URL'deki boşlukları vb kodlayarak düzgün link yapalım
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
