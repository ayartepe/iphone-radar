import streamlit as st
import sqlite3
import pandas as pd
import os

st.set_page_config(page_title="Cem's Radar", page_icon="📱", layout="wide")

st.title("📱 Cem's iPhone Piyasa Radarı")

def verileri_getir():
    db_path = os.path.join(os.getcwd(), 'fiyat_takip.db')
    if not os.path.exists(db_path):
        st.error("⚠️ Veritabanı bulunamadı!")
        return None
    try:
        conn = sqlite3.connect(db_path, check_same_thread=False)
        df = pd.read_sql_query("SELECT isim, son_fiyat, degisim FROM urunler ORDER BY son_fiyat ASC", conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"❌ Hata: {e}")
        return None

df = verileri_getir()

if df is not None and not df.empty:
    # 1. Renklendirme Fonksiyonu (Hatalı kısım burasıydı, düzelttik)
    def color_degisim(val):
        # Eğer değer sayıysa kıyasla, değilse boş dön
        try:
            num = float(str(val).replace(' TL', '').replace(',', '').replace('+', ''))
            if num < 0: return 'color: #00ff00; font-weight: bold'
            if num > 0: return 'color: #ff4b4b; font-weight: bold'
        except:
            pass
        return 'color: #808080'

    # 2. Tabloyu Hazırlama
    display_df = df.copy()
    display_df['Durum'] = display_df['degisim'].apply(lambda x: "📉 İndirim" if x < 0 else ("🔺 Zam" if x > 0 else "➖ Sabit"))
    
    # Görsel formatlama (TL ekleme vs)
    display_df['son_fiyat_gosterim'] = display_df['son_fiyat'].apply(lambda x: f"{int(x):,} TL")
    display_df['Fiyat Farkı'] = display_df['degisim'].apply(lambda x: f"{'+' if x>0 else ''}{int(x):,} TL")

    # 3. Tabloyu Göster (Sadece seçtiğimiz sütunları ve renkleri uygula)
    st.subheader("📊 Canlı Fiyat Takip Listesi")
    
    # ÖNEMLİ: Renklendirmeyi sadece 'Fiyat Farkı' sütununa uygula
    st.dataframe(
        display_df[['Durum', 'isim', 'son_fiyat_gosterim', 'Fiyat Farkı']].style.applymap(
            color_degisim, subset=['Fiyat Farkı']
        ), 
        use_container_width=True, hide_index=True
    )
    
    st.divider()
    st.metric("Takip Edilen Ürün", len(df))

else:
    st.info("Veriler yükleniyor...")

if st.button('🔄 Yenile'):
    st.rerun()