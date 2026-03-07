import streamlit as st
import sqlite3
import pandas as pd
import os

st.set_page_config(page_title="Cem's Radar", page_icon="📱", layout="wide")

st.title("📱 Cem's iPhone Piyasa Radarı")

def verileri_getir():
    # Dosya yolunu garantiye alalım
    db_path = os.path.join(os.getcwd(), 'fiyat_takip.db')
    
    if not os.path.exists(db_path):
        st.error(f"⚠️ Kritik Hata: 'fiyat_takip.db' dosyası bulunamadı. Lütfen GitHub deponuzun ana dizininde bu isimde bir dosya olduğundan emin olun.")
        st.info(f"Aranan yol: {db_path}")
        return None
    
    try:
        # check_same_thread=False Streamlit'in eşzamanlı çalışması için önemli
        conn = sqlite3.connect(db_path, check_same_thread=False)
        df = pd.read_sql_query("SELECT isim, son_fiyat, degisim FROM urunler ORDER BY son_fiyat ASC", conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"❌ Veritabanı Okuma Hatası: {e}")
        return None

df = verileri_getir()

if df is not None and not df.empty:
    # Renklendirme fonksiyonu
    def color_degisim(val):
        if val < 0: return 'color: #00ff00; font-weight: bold'
        elif val > 0: return 'color: #ff4b4b; font-weight: bold'
        return 'color: #808080'

    # Tablo hazırlığı
    display_df = df.copy()
    display_df['Durum'] = display_df['degisim'].apply(lambda x: "📉 İndirim" if x < 0 else ("🔺 Zam" if x > 0 else "➖ Sabit"))
    display_df['son_fiyat'] = display_df['son_fiyat'].apply(lambda x: f"{int(x):,} TL")
    display_df['Fiyat Farkı'] = display_df['degisim'].apply(lambda x: f"{'+' if x>0 else ''}{int(x):,} TL")

    st.subheader("📊 Canlı Fiyat Takip Listesi")
    st.dataframe(
        display_df[['Durum', 'isim', 'son_fiyat', 'Fiyat Farkı']].style.applymap(
            color_degisim, subset=['Fiyat Farkı']
        ), 
        use_container_width=True, hide_index=True
    )
    
    # Özet kartları
    st.divider()
    indirim_sayisi = len(df[df['degisim'] < 0])
    st.metric("İndirimdeki Ürün Sayısı", f"{indirim_sayisi} Adet")

else:
    if df is not None:
        st.warning("Veritabanı bulundu ama içi henüz boş. Lütfen botun veri toplamasını bekleyin.")

if st.button('🔄 Verileri Güncelle'):
    st.rerun()