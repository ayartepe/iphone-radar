import telebot
from curl_cffi import requests
from bs4 import BeautifulSoup
import sqlite3
import time

TOKEN = "8676649786:AAGnpP4Qu_G6vwNYBck9ty4YlhEgNwvijCw"
CHAT_ID = 7701768698
bot = telebot.TeleBot(TOKEN)

def db_kur():
    conn = sqlite3.connect('fiyat_takip.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS urunler 
                 (isim TEXT PRIMARY KEY, son_fiyat REAL)''')
    conn.commit()
    conn.close()

def fiyat_kontrol_ve_kaydet(urun_adi, yeni_fiyat, site_adi):
    conn = sqlite3.connect('fiyat_takip.db')
    c = conn.cursor()
    c.execute("SELECT son_fiyat FROM urunler WHERE isim=?", (urun_adi,))
    row = c.fetchone()
    
    bildirim_gonder = False
    mesaj_detay = ""

    if row is None:
        c.execute("INSERT INTO urunler VALUES (?, ?)", (urun_adi, yeni_fiyat))
        print(f"[{site_adi}] Yeni ürün hafızaya alındı: {urun_adi}")
    else:
        eski_fiyat = row[0]
        if yeni_fiyat < eski_fiyat:
            fark = eski_fiyat - yeni_fiyat
            mesaj_detay = f"📉 *{site_adi} İndirimi!* \nÖnceki: {eski_fiyat:,} TL\nYeni: {yeni_fiyat:,} TL\nFark: *{fark:,} TL ucuzladı!*"
            bildirim_gonder = True
            c.execute("UPDATE urunler SET son_fiyat=? WHERE isim=?", (yeni_fiyat, urun_adi))
            print(f"[{site_adi}] İndirim tespit edildi!")
        else:
            c.execute("UPDATE urunler SET son_fiyat=? WHERE isim=?", (yeni_fiyat, urun_adi))
    
    conn.commit()
    conn.close()
    return bildirim_gonder, mesaj_detay

def amazon_tara():
    # Amazon Türkiye iPhone araması
    url = 'https://www.amazon.com.tr/s?k=iphone'
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"}
    
    try:
        response = requests.get(url, headers=headers, impersonate="chrome110")
        soup = BeautifulSoup(response.content, 'html.parser')
        # Amazon'un ürün blokları
        items = soup.find_all('div', {'data-component-type': 's-search-result'})
        
        for item in items[:5]:
            name = item.find('h2').get_text(strip=True)
            price_whole = item.find('span', {'class': 'a-price-whole'})
            if price_whole:
                price = int(price_whole.get_text(strip=True).replace(".", "").replace(",", ""))
                dustu_mu, detay = fiyat_kontrol_ve_kaydet(name, price, "Amazon")
                if dustu_mu:
                    bot.send_message(CHAT_ID, f"🏗 *AMAZON RADARI*\n\n📱 {name}\n{detay}\n\n🔗 [Amazon'da Gör]({url})", parse_mode="Markdown")
    except Exception as e:
        print(f"Amazon Hatası: {e}")

def cimri_tara():
    url = 'https://www.cimri.com/cep-telefonlari/en-ucuz-iphone-fiyatlari'
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"}
    
    try:
        response = requests.get(url, headers=headers, impersonate="chrome110")
        soup = BeautifulSoup(response.content, 'html.parser')
        items = soup.find_all('article')
        
        for item in items[:10]:
            name = item.find('h3').get_text(strip=True)
            price_text = ""
            for p_tag in item.find_all(['div', 'span', 'p']):
                t = p_tag.get_text(strip=True)
                if 'TL' in t and any(c.isdigit() for c in t):
                    price_text = t.split(",")[0].replace(".", "").replace("TL", "").strip()
                    break
            
            if price_text:
                price = int(price_text)
                dustu_mu, detay = fiyat_kontrol_ve_kaydet(name, price, "Cimri")
                if dustu_mu:
                    bot.send_message(CHAT_ID, f"🎯 *CİMRİ RADARI*\n\n📱 {name}\n{detay}\n\n🔗 [Cimri'de Gör]({url})", parse_mode="Markdown")
    except Exception as e:
        print(f"Cimri Hatası: {e}")

# BAŞLAT
db_kur()
print("Cem's Multi-Radar v2.5 (Amazon + Cimri) Aktif...")
while True:
    amazon_tara()
    cimri_tara()
    print("Taramalar bitti. 10 dakika pusuda bekleniyor...")
    time.sleep(600)