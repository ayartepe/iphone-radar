import streamlit as st
import sqlite3
import pandas as pd
import os

st.set_page_config(page_title="Cem's Radar", page_icon="📱", layout="wide")

# Başlık ve Açıklama
st.title("📱 Cem's iPhone Piyasa Radarı")
st.markdown("Piyasadaki en güncel iPhone fiyatlarını ve indirimlerini takip edin.")

def verileri_getir():
    db_path = os.path.join(os.getcwd(), 'fiyat_takip.db')
    if not os.path.exists(db_path):
        return None
    try:
        conn = sqlite3.connect(db_path, check_same_thread=False)
        df = pd.read_sql_query("SELECT isim, son_fiyat, degisim, son_indirim_tarihi FROM urunler", conn)
        conn.close()
        return df
    except:
        return None

df = verileri_getir()

if df is not None and not df.empty:
    # --- Üst İstatistik Kartları ---
    indirimdeki_urunler = df[df['degisim'] < 0]
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Toplam Ürün", len(df))
    col2.metric("İndirimdekiler", len(indirimdeki_urunler), delta=None)
    col3.info("Tarama Sıklığı: 1 Saat")

    # --- Filtreleme Alanı ---
    st.divider()
    arama_terimi = st.text_input("🔍 Ürün Ara (Örn: iPhone 16 Pro)", "").lower()
    
    # Veriyi filtrele
    filtered_df = df[df['isim'].str.lower().str.contains(arama_terimi)].copy()
    # Fiyata göre sırala (En ucuz en üstte)
    filtered_df = filtered_df.sort_values(by='son_fiyat', ascending=True)

    # --- Görsel Hazırlık ---
    def color_degisim(val):
        try:
            num = float(str(val).replace(' TL', '').replace(',', '').replace('+', ''))
            if num < 0: return 'background-color: #d4edda; color: #155724; font-weight: bold' # Yeşil arka plan
            if num > 0: return 'color: #721c24;' # Kırmızı yazı
        except: pass
        return ''

    # Tabloyu formatla
    display_df = filtered_df.copy()
    display_df['Durum'] = display_df['degisim'].apply(lambda x: "📉 İNDİRİM" if x < 0 else ("🔺 Zam" if x > 0 else "➖ Sabit"))
    display_df['Fiyat'] = display_df['son_fiyat'].apply(lambda x: f"{int(x):,} TL")
    display_df['Fark'] = display_df['degisim'].apply(lambda x: f"{'+' if x>0 else ''}{int(x):,} TL" if x != 0 else "---")
    display_df = display_df.rename(columns={'isim': 'Ürün Adı', 'son_indirim_tarihi': 'Son Güncelleme'})

    # --- Tabloyu Göster ---
    st.dataframe(
        display_df[['Durum', 'Ürün Adı', 'Fiyat', 'Fark', 'Son Güncelleme']].style.applymap(
            color_degisim, subset=['Fark']
        ), 
        use_container_width=True, hide_index=True
    )
    
    if len(filtered_df) == 0:
        st.warning("Aradığınız kriterlere uygun ürün bulunamadı.")
else:
    st.warning("Veritabanı henüz hazır değil. Lütfen botun ilk taramasını bitirip .db dosyasını yüklemesini bekleyin.")

if st.sidebar.button('🔄 Sayfayı Yenile'):
    st.rerun()