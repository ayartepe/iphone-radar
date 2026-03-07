import streamlit as st
import sqlite3
import pandas as pd
import os

st.set_page_config(page_title="Cem's Radar", page_icon="📱", layout="wide")

st.title("📱 Cem's iPhone Piyasa Radarı")

def verileri_getir():
    db_path = os.path.join(os.getcwd(), 'fiyat_takip.db')
    if not os.path.exists(db_path):
        return None
    
    conn = sqlite3.connect(db_path)
    try:
        df = pd.read_sql_query("SELECT isim, son_fiyat, degisim FROM urunler ORDER BY son_fiyat ASC", conn)
    except:
        df = None
    finally:
        conn.close()
    return df

df = verileri_getir()

if df is not None and not df.empty:
    # Renklendirme mantığı
    def color_degisim(val):
        if val < 0: return 'color: #00ff00; font-weight: bold'
        elif val > 0: return 'color: #ff4b4b; font-weight: bold'
        return 'color: gray'

    styled_df = df.copy()
    styled_df['Durum'] = styled_df['degisim'].apply(lambda x: "📉 İndirim" if x < 0 else ("🔺 Zam" if x > 0 else "➖ Sabit"))
    styled_df['son_fiyat'] = styled_df['son_fiyat'].apply(lambda x: f"{int(x):,} TL")
    styled_df['Fiyat Farkı'] = styled_df['degisim'].apply(lambda x: f"{'+' if x>0 else ''}{int(x):,} TL")

    st.dataframe(
        styled_df[['Durum', 'isim', 'son_fiyat', 'Fiyat Farkı']].style.applymap(
            color_degisim, subset=['Fiyat Farkı']
        ), 
        use_container_width=True, hide_index=True
    )
    
    # Özet kartı
    indirimler = df[df['degisim'] < 0]
    if not indirimler.empty:
        st.success(f"🔥 Şu an {len(indirimler)} üründe indirim var!")
else:
    st.warning("Veritabanı henüz hazır değil. Lütfen ana botu çalıştırıp 'fiyat_takip.db' dosyasını yükleyin.")

if st.button('🔄 Yenile'):
    st.rerun()