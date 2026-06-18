import streamlit as st
import fitz
import io
import zipfile

# --- 1. AYARLAR ---
st.set_page_config(page_title="PDF Asistanım", layout="wide", page_icon="📄")

# KESİN ÇÖZÜM: NEON KART TASARIMI
st.markdown("""
    <style>
    /* Genel uygulama metin rengi */
    .stApp, p, h1, h2, h3, .stCaption {
        color: var(--text-color) !important;
    }

    /* BUTON KAPSAYICISINI (KUTUYU) HEDEF ALIYORUZ */
    div.stButton {
        text-align: center;
        margin-bottom: 10px;
    }

    /* Butonun kendisini gerçek bir NEON kutuya çeviriyoruz */
    div.stButton > button {
        background-color: #1a1c24 !important; /* Koyu, şık bir buton arka planı */
        color: #00f3ff !important;           /* Neon Turkuaz metin rengi */
        border: 2px solid #00f3ff !important; /* Neon Turkuaz çerçeve */
        border-radius: 15px !important;
        height: 150px !important;
        width: 100% !important;
        font-weight: bold !important;
        font-size: 20px !important;
        /* Neon Parlama Efekti */
        box-shadow: 0 0 10px #00f3ff, inset 0 0 5px #00f3ff !important;
        transition: all 0.3s ease-in-out !important;
        display: block !important;
    }

    /* Üzerine gelince parlama artar ve renk dolar */
    div.stButton > button:hover {
        background-color: #00f3ff !important;
        color: #000000 !important;           /* Yazı siyah olur */
        box-shadow: 0 0 30px #00f3ff !important;
        transform: translateY(-5px) !important;
    }

    /* Sidebar düzenlemesi */
    [data-testid="stSidebar"] {
        background-color: var(--secondary-background-color) !important;
        border-right: 1px solid #00f3ff;
    }
    
    /* Alt bilgilendirme çubuğu */
    .footer-note {
        padding: 10px;
        border-radius: 10px;
        background-color: rgba(0, 243, 255, 0.1);
        border: 1px solid #00f3ff;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. FONKSİYONLAR ---
def pdf_onizle(dosya):
    doc = fitz.open(stream=dosya.read(), filetype="pdf")
    page = doc.load_page(0)
    pix = page.get_pixmap(matrix=fitz.Matrix(0.5, 0.5))
    img = io.BytesIO(pix.tobytes("png"))
    st.image(img, caption="Dosya Önizlemesi", width=200)
    dosya.seek(0)

def islem_yap(dosya, islem_tipi, parametre=None, aci=90):
    doc = fitz.open(stream=dosya.read(), filetype="pdf")
    if islem_tipi == 'Döndür':
        for page in doc: page.set_rotation(int(aci))
        cikti = io.BytesIO(); doc.save(cikti)
        return cikti.getvalue(), "pdf"
    elif islem_tipi == 'Böl':
        if not parametre or parametre.strip() == "":
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zf:
                for i in range(len(doc)):
                    yeni_doc = fitz.open(); yeni_doc.insert_pdf(doc, from_page=i, to_page=i)
                    zf.writestr(f"sayfa_{i+1}.pdf", yeni_doc.write())
            return zip_buffer.getvalue(), "zip"
        else:
            sayfa_no = int(parametre) - 1
            yeni_doc = fitz.open(); yeni_doc.insert_pdf(doc, from_page=sayfa_no, to_page=sayfa_no)
            return yeni_doc.write(), "pdf"
    elif islem_tipi == 'Sayfa Sil':
        sil_no = int(parametre) - 1
        yeni_doc = fitz.open()
        for i in range(len(doc)):
            if i != sil_no: yeni_doc.insert_pdf(doc, from_page=i, to_page=i)
        return yeni_doc.write(), "pdf"

# --- 3. ARAYÜZ ---
if 'page' not in st.session_state: st.session_state.page = 'home'

with st.sidebar:
    st.title("📄 PDF Asistanım")
    st.metric(label="🚀 Toplam İşlenen PDF", value="1.240+")
    st.info("🔒 **Güvenlik Hatırlatması:** Yüklediğiniz dosyalar sunucuda **kayıt altına alınmaz.** İşlem bittiğinde dosyalar geçici bellekten tamamen silinir.")
    st.write("---")
    if st.session_state.page != 'home':
        if st.button("🏠 Ana Menüye Dön"): 
            st.session_state.page = 'home'
            st.rerun()

if st.session_state.page == 'home':
    st.title("📄 PDF Asistanım")
    st.subheader("Hızlı, Güvenli ve Profesyonel PDF Araçları")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✂️ PDF BÖL"): st.session_state.page = 'Böl'; st.rerun()
        st.caption("PDF dosyanızı sayfalara ayırın.")
        if st.button("🔄 DÖNDÜR"): st.session_state.page = 'Döndür'; st.rerun()
        st.caption("PDF sayfalarınızı döndürün.")
    with col2:
        if st.button("🔗 BİRLEŞTİR"): st.session_state.page = 'Birleştir'; st.rerun()
        st.caption("PDF dosyalarınızı tek dosyada birleştirin.")
        if st.button("🗑️ SAYFA SİL"): st.session_state.page = 'Sayfa Sil'; st.rerun()
        st.caption("İstediğiniz sayfaları PDF'den çıkarın.")
    
    st.write("")
    st.markdown('<div class="footer-note">🛡️ <b>Gizlilik Notu:</b> İşlem yaptığınız PDF dosyaları sunucuda saklanmaz ve kimseyle paylaşılmaz.</div>', unsafe_allow_html=True)

else:
    st.header(f"Araç: {st.session_state.page}")
    st.write("---")
    
    with st.expander("📖 Bilgilendirme ve Güvenlik"):
        st.write("1. Dosyanızı yükleyin.\n2. Gerekli ayarları seçin.\n3. '🚀 İşlemi Başlat' butonuna basın.")
        st.warning("🛡️ **Önemli:** Verileriniz geçici bellekte işlenir. Sayfayı yenilediğinizde veya oturum bittiğinde her şey silinir.")

    dosya = st.file_uploader("PDF dosyanızı yükleyin", type="pdf", accept_multiple_files=(st.session_state.page == "Birleştir"))
    
    if dosya:
        if st.session_state.page != "Birleştir": pdf_onizle(dosya)
        parametre = st.text_input("İşlem yapılacak sayfa numarası:") if st.session_state.page in ["Böl", "Sayfa Sil"] else None
        aci = st.selectbox("Döndürme Açısı Seçin:", [90, 180, 270, 360]) if st.session_state.page == "Döndür" else 90
        
        if st.button("🚀 İşlemi Başlat"):
            with st.spinner("Dosyanız işleniyor..."):
                if st.session_state.page == "Birleştir":
                    yazici = fitz.open()
                    for d in dosya: yazici.insert_pdf(fitz.open(stream=d.read(), filetype="pdf"))
                    sonuc = io.BytesIO(); yazici.save(sonuc); sonuc = sonuc.getvalue(); tur = "pdf"
                else: sonuc, tur = islem_yap(dosya, st.session_state.page, parametre, aci)
                
                st.success("İşlem Başarıyla Tamamlandı!")
                st.download_button("📥 İşlenmiş Dosyayı İndir", sonuc, f"asistan_sonuc.{tur}")