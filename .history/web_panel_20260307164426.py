import streamlit as st
import sqlite3
import pandas as pd
import os

st.set_page_config(page_title="Cem's Radar", page_icon="📱", layout="wide")
st.title("📱 Cem's iPhone Piyasa Radarı")

def verileri_getir():
    db_path = os.path.join(os.getcwd(), 'fiyat_takip.db')
    if not os.path.exists(db_path): return None
    try:
        conn = sqlite3.connect(db_path, check_same_thread=False)
        # Yeni sütunu da çekiyoruz
        df = pd.read_sql_query("SELECT isim, son_fiyat, degisim, son_indirim_tarihi FROM urunler ORDER BY son_fiyat ASC", conn)
        conn.close()
        return df
    except: return None

df = verileri_getir()

if df is not None and not df.empty:
    display_df = df.copy()
    
    # Renklendirme ve İkonlar
    display_df['Durum'] = display_df['degisim'].apply(lambda x: "📉 İNDİRİM" if x < 0 else ("🔺 Zam" if x > 0 else "➖ Sabit"))
    display_df['Fiyat'] = display_df['son_fiyat'].apply(lambda x: f"{int(x):,} TL")
    display_df['Değişim'] = display_df['degisim'].apply(lambda x: f"{int(x):,} TL" if x != 0 else "---")
    display_df['Yakalanma Zamanı'] = display_df['son_indirim_tarihi']

    # Şık Tablo
    st.dataframe(
        display_df[['Durum', 'isim', 'Fiyat', 'Değişim', 'Yakalanma Zamanı']],
        use_container_width=True, hide_index=True
    )
    
    st.info("💡 Not: İndirimler, fiyat tekrar yükselene kadar listede 'Yakalanma Zamanı' ile birlikte saklanır.")
else:
    st.warning("Veritabanı güncelleniyor...")

if st.button('🔄 Manuel Yenile'):
    st.rerun()