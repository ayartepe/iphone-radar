import streamlit as st
import sqlite3
import pandas as pd

# Sayfa Ayarları
st.set_page_config(page_title="Cem's iPhone Radar", page_icon="📱", layout="wide")

st.title("📱 Cem's iPhone Piyasa Radarı")
st.markdown("---")

# Veritabanından Verileri Çek
def verileri_getir():
    conn = sqlite3.connect('fiyat_takip.db')
    df = pd.read_sql_query("SELECT * FROM urunler ORDER BY son_fiyat ASC", conn)
    conn.close()
    return df

try:
    df = verileri_getir()
    
    # Üst Bilgi Kartları (Metrikler)
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Takip Edilen Ürün", len(df))
    with col2:
        en_ucuz = df.iloc[0]
        st.metric("Günün En Ucuz Fiyatı", f"{int(en_ucuz['son_fiyat']):,} TL")

    # Ana Tablo
    st.subheader("📊 Güncel Fiyat Listesi")
    st.dataframe(df, use_container_width=True)

    # Basit bir Fiyat Dağılım Grafiği
    st.subheader("📈 Fiyat Dağılımı")
    st.bar_chart(df.set_index('isim')['son_fiyat'])

except Exception as e:
    st.error("Henüz veritabanında veri yok veya bot taranıyor...")
    st.info("Lütfen önce ana botu çalıştırıp verilerin dolmasını bekle.")

# Otomatik yenileme butonu
if st.button('Piyasayı Yenile'):
    st.rerun()