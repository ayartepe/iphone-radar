import telebot
from curl_cffi import requests
from bs4 import BeautifulSoup
import sqlite3
import time
from datetime import datetime

# --- AYARLAR ---
TOKEN = "8676649786:AAGnpP4Qu_G6vwNYBck9ty4YlhEgNwvijCw"
CHAT_ID = 7701768698
bot = telebot.TeleBot(TOKEN)

def db_kur():
    conn = sqlite3.connect('fiyat_takip.db')
    c = conn.cursor()
    # 'son_indirim_tarihi' sütununu ekledik
    c.execute('''CREATE TABLE IF NOT EXISTS urunler 
                 (isim TEXT PRIMARY KEY, son_fiyat REAL, degisim REAL DEFAULT 0, son_indirim_tarihi TEXT)''')
    conn.commit()
    conn.close()

def fiyat_kontrol_ve_kaydet(urun_adi, yeni_fiyat, site_adi):
    conn = sqlite3.connect('fiyat_takip.db')
    c = conn.cursor()
    c.execute("SELECT son_fiyat, degisim, son_indirim_tarihi FROM urunler WHERE isim=?", (urun_adi,))
    row = c.fetchone()
    
    bildirim_gonder = False
    simdi = datetime.now().strftime('%d/%m %H:%M')

    if row is None:
        c.execute("INSERT INTO urunler (isim, son_fiyat, degisim, son_indirim_tarihi) VALUES (?, ?, ?, ?)", 
                  (urun_adi, yeni_fiyat, 0, "Yeni Kayıt"))
    else:
        eski_fiyat, eski_degisim, eski_tarih = row
        
        if yeni_fiyat < eski_fiyat:
            # Fiyat düştü! Yeni farkı ve tarihi kaydet.
            degisim_miktari = yeni_fiyat - eski_fiyat
            c.execute("UPDATE urunler SET son_fiyat=?, degisim=?, son_indirim_tarihi=? WHERE isim=?", 
                      (yeni_fiyat, degisim_miktari, simdi, urun_adi))
            bildirim_gonder = True
        elif yeni_fiyat > eski_fiyat:
            # Fiyat arttı! Hafızayı sıfırla (indirim bitti)
            c.execute("UPDATE urunler SET son_fiyat=?, degisim=?, son_indirim_tarihi=? WHERE isim=?", 
                      (yeni_fiyat, 0, "Fiyat Arttı", urun_adi))
        else:
            # Fiyat aynı! Eğer önceden bir indirim varsa onu ve tarihini koru.
            c.execute("UPDATE urunler SET son_fiyat=? WHERE isim=?", (yeni_fiyat, urun_adi))
    
    conn.commit()
    conn.close()
    return bildirim_gonder

# ... (amazon_tara ve cimri_tara fonksiyonları aynı kalıyor, sadece fonksiyon çağrısını 'fiyat_kontrol_ve_kaydet'e göre yapıyoruz) ...

def amazon_tara():
    url = 'https://www.amazon.com.tr/s?k=iphone'
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"}
    try:
        response = requests.get(url, headers=headers, impersonate="chrome110")
        soup = BeautifulSoup(response.content, 'html.parser')
        items = soup.find_all('div', {'data-component-type': 's-search-result'})
        for item in items[:5]:
            name_tag = item.find('h2')
            if not name_tag: continue
            name = name_tag.get_text(strip=True)[:50]
            price_whole = item.find('span', {'class': 'a-price-whole'})
            if price_whole:
                price = int(price_whole.get_text(strip=True).replace(".", "").replace(",", ""))
                if fiyat_kontrol_ve_kaydet(name, price, "Amazon"):
                    bot.send_message(CHAT_ID, f"🏗 *AMAZON İNDİRİMİ*\n\n📱 {name}\n💰 Yeni Fiyat: {price:,} TL", parse_mode="Markdown")
    except Exception as e: print(f"Amazon Hatası: {e}")

def cimri_tara():
    url = 'https://www.cimri.com/cep-telefonlari/en-ucuz-iphone-fiyatlari'
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"}
    try:
        response = requests.get(url, headers=headers, impersonate="chrome110")
        soup = BeautifulSoup(response.content, 'html.parser')
        items = soup.find_all('article')
        for item in items[:10]:
            name_tag = item.find('h3')
            if not name_tag: continue
            name = name_tag.get_text(strip=True)[:50]
            price_text = ""
            for p_tag in item.find_all(['div', 'span', 'p']):
                t = p_tag.get_text(strip=True)
                if 'TL' in t and any(c.isdigit() for c in t):
                    price_text = t.split(",")[0].replace(".", "").replace("TL", "").strip()
                    break
            if price_text:
                price = int(price_text)
                if fiyat_kontrol_ve_kaydet(name, price, "Cimri"):
                    bot.send_message(CHAT_ID, f"🎯 *CİMRİ İNDİRİMİ*\n\n📱 {name}\n💰 Yeni Fiyat: {price:,} TL", parse_mode="Markdown")
    except Exception as e: print(f"Cimri Hatası: {e}")

db_kur()
while True:
    print(f"[{time.strftime('%H:%M:%S')}] Saatlik tarama başlıyor...")
    amazon_tara()
    cimri_tara()
    print("İşlem bitti, 1 saat uyku moduna geçiliyor.")
    time.sleep(3600) # 1 saat