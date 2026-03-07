import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="Cem's Radar", page_icon="📱", layout="wide")

st.title("📱 Cem's iPhone Piyasa Radarı")
st.markdown("Veriler anlık olarak **Amazon** ve **Cimri** üzerinden çekilip analiz edilmektedir.")

def verileri_getir():
    conn = sqlite3.connect('fiyat_takip.db')
    # İsme göre sıralı getir
    df = pd.read_sql_query("SELECT isim, son_fiyat, degisim FROM urunler ORDER BY son_fiyat ASC", conn)
    conn.close()
    return df

try:
    df = verileri_getir()

    # Tabloyu hazırlama
    st.subheader("📊 Canlı Fiyat Takip Çizelgesi")
    
    # Görselleştirmeyi iyileştirelim
    def color_degisim(val):
        if val < 0:
            return 'color: #00ff00; font-weight: bold' # Yeşil
        elif val > 0:
            return 'color: #ff4b4b; font-weight: bold' # Kırmızı
        else:
            return 'color: #808080' # Gri

    # Kopya oluşturup formatlayalım
    styled_df = df.copy()
    
    # Durum ikonu ekleyelim
    styled_df['Durum'] = styled_df['degisim'].apply(lambda x: "📉 İndirim" if x < 0 else ("🔺 Zam" if x > 0 else "➖ Sabit"))
    
    # Gösterim formatı
    styled_df['son_fiyat'] = styled_df['son_fiyat'].apply(lambda x: f"{int(x):,} TL")
    styled_df['Fiyat Farkı'] = styled_df['degisim'].apply(lambda x: f"{'+' if x>0 else ''}{int(x):,} TL")

    # Tabloyu bastır
    st.dataframe(
        styled_df[['Durum', 'isim', 'son_fiyat', 'Fiyat Farkı']].style.applymap(
            color_degisim, subset=['Fiyat Farkı']
        ), 
        use_container_width=True,
        hide_index=True
    )

    # Özet Kartları
    st.markdown("---")
    c1, c2 = st.columns(2)
    indirimdekiler = df[df['degisim'] < 0]
    c1.metric("İndirimdeki Ürün Sayısı", len(indirimdekiler))
    if not indirimdekiler.empty:
        en_buyuk_firsat = indirimdekiler.iloc[indirimdekiler['degisim'].idxmin()]
        c2.success(f"Günün Fırsatı: {en_buyuk_firsat['isim']} ({abs(en_buyuk_firsat['degisim']):,} TL düşüş!)")

except Exception as e:
    st.warning("Veriler yükleniyor, lütfen bekleyin...")
    # st.write(e) # Hata ayıklamak istersen açabilirsin

if st.button('🔄 Sayfayı Yenile'):
    st.rerun()