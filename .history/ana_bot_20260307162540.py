import telebot
from curl_cffi import requests
from bs4 import BeautifulSoup
import sqlite3
import time

# --- AYARLARIN ---
TOKEN = "8676649786:AAGnpP4Qu_G6vwNYBck9ty4YlhEgNwvijCw"
CHAT_ID = 7701768698
bot = telebot.TeleBot(TOKEN)

def db_kur():
    conn = sqlite3.connect('fiyat_takip.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS urunler 
                 (isim TEXT PRIMARY KEY, son_fiyat REAL, degisim REAL DEFAULT 0)''')
    conn.commit()
    conn.close()

def fiyat_kontrol_ve_kaydet(urun_adi, yeni_fiyat, site_adi):
    conn = sqlite3.connect('fiyat_takip.db')
    c = conn.cursor()
    c.execute("SELECT son_fiyat FROM urunler WHERE isim=?", (urun_adi,))
    row = c.fetchone()
    bildirim_gonder = False
    degisim_miktari = 0

    if row is None:
        c.execute("INSERT INTO urunler (isim, son_fiyat, degisim) VALUES (?, ?, ?)", (urun_adi, yeni_fiyat, 0))
    else:
        eski_fiyat = row[0]
        degisim_miktari = yeni_fiyat - eski_fiyat
        c.execute("UPDATE urunler SET son_fiyat=?, degisim=? WHERE isim=?", (yeni_fiyat, degisim_miktari, urun_adi))
        if yeni_fiyat < eski_fiyat:
            bildirim_gonder = True
    
    conn.commit()
    conn.close()
    return bildirim_gonder, degisim_miktari

def amazon_tara():
    url = 'https://www.amazon.com.tr/s?k=iphone'
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"}
    try:
        response = requests.get(url, headers=headers, impersonate="chrome110")
        soup = BeautifulSoup(response.content, 'html.parser')
        items = soup.find_all('div', {'data-component-type': 's-search-result'})
        for item in items[:5]:
            name = item.find('h2').get_text(strip=True)[:50]
            price_whole = item.find('span', {'class': 'a-price-whole'})
            if price_whole:
                price = int(price_whole.get_text(strip=True).replace(".", "").replace(",", ""))
                dustu, fark = fiyat_kontrol_ve_kaydet(name, price, "Amazon")
                if dustu:
                    bot.send_message(CHAT_ID, f"🏗 *AMAZON İNDİRİMİ*\n\n📱 {name}\n💰 Fiyat: {price:,} TL\n📉 Düşüş: {abs(fark):,} TL", parse_mode="Markdown")
    except Exception as e: print(f"Amazon Hatası: {e}")

def cimri_tara():
    url = 'https://www.cimri.com/cep-telefonlari/en-ucuz-iphone-fiyatlari'
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"}
    try:
        response = requests.get(url, headers=headers, impersonate="chrome110")
        soup = BeautifulSoup(response.content, 'html.parser')
        items = soup.find_all('article')
        for item in items[:10]:
            name = item.find('h3').get_text(strip=True)[:50]
            price_text = ""
            for p_tag in item.find_all(['div', 'span', 'p']):
                t = p_tag.get_text(strip=True)
                if 'TL' in t and any(c.isdigit() for c in t):
                    price_text = t.split(",")[0].replace(".", "").replace("TL", "").strip()
                    break
            if price_text:
                price = int(price_text)
                dustu, fark = fiyat_kontrol_ve_kaydet(name, price, "Cimri")
                if dustu:
                    bot.send_message(CHAT_ID, f"🎯 *CİMRİ İNDİRİMİ*\n\n📱 {name}\n💰 Fiyat: {price:,} TL\n📉 Düşüş: {abs(fark):,} TL", parse_mode="Markdown")
    except Exception as e: print(f"Cimri Hatası: {e}")

db_kur()
while True:
    print(f"[{time.strftime('%H:%M:%S')}] Taramalar yapılıyor...")
    amazon_tara()
    cimri_tara()
    time.sleep(600)