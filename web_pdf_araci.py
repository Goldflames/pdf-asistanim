import streamlit as st
import fitz
import io
import zipfile
from PIL import Image

# --- 1. AYARLAR ---
st.set_page_config(page_title="PDF Asistanım", layout="wide", page_icon="📄")

st.markdown("""
    <style>
    /* ANA BUTONLAR: Sabit genişlik ve hizalama */
    div.stButton > button {
        width: 100% !important; min-width: 300px !important; height: 80px !important;
        border-radius: 15px !important; background-color: #1a1c24 !important;
        color: #00f3ff !important; border: 2px solid #00f3ff !important;
        box-shadow: 0 0 10px #00f3ff !important; font-weight: bold !important;
        font-size: 15px !important; transition: all 0.3s ease !important;
    }
    [data-testid="stSidebar"] div.stButton > button {
        height: 45px !important; font-size: 13px !important; width: auto !important; 
        min-width: 150px !important; margin: 0 auto !important;
    }
    div.stButton > button:hover {
        background-color: #00f3ff !important; color: #000000 !important;
        box-shadow: 0 0 25px #00f3ff !important;
    }
    .footer-note { 
        padding: 15px; border-radius: 10px; background-color: rgba(0, 243, 255, 0.05); 
        border: 1px solid #00f3ff; text-align: center; margin-top: 50px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. FONKSİYONLAR ---
def pdf_onizle(dosya):
    doc = fitz.open(stream=dosya.read(), filetype="pdf")
    page = doc.load_page(0)
    pix = page.get_pixmap(matrix=fitz.Matrix(0.5, 0.5))
    img = io.BytesIO(pix.tobytes("png"))
    st.image(img, caption="Önizleme", width=200)
    dosya.seek(0)

def pdf_birlestir(dosyalar):
    yeni_doc = fitz.open()
    progress_bar = st.progress(0)
    for i, dosya in enumerate(dosyalar):
        doc = fitz.open(stream=dosya.read(), filetype="pdf")
        yeni_doc.insert_pdf(doc)
        progress_bar.progress((i + 1) / len(dosyalar))
    cikti = io.BytesIO()
    yeni_doc.save(cikti)
    return cikti.getvalue()

def pdf_duzelt(dosya):
    doc = fitz.open(stream=dosya.read(), filetype="pdf")
    progress_bar = st.progress(0)
    for i, page in enumerate(doc):
        page.set_rotation(0) # Rotasyonu sıfırlayarak düzeltme
        progress_bar.progress((i + 1) / len(doc))
    cikti = io.BytesIO()
    doc.save(cikti)
    return cikti.getvalue()

def jpg_to_a4_pdf(img1, img2=None):
    pdf_output = io.BytesIO()
    c = Image.new('RGB', (2480, 3508), 'white')
    p1 = Image.open(img1).convert('RGB').resize((2200, 1500))
    c.paste(p1, (140, 200))
    if img2:
        p2 = Image.open(img2).convert('RGB').resize((2200, 1500))
        c.paste(p2, (140, 1800))
    c.save(pdf_output, "PDF", resolution=100.0)
    return pdf_output.getvalue()

def islem_yap(dosya, islem_tipi, parametre=None, aci=90):
    doc = fitz.open(stream=dosya.read(), filetype="pdf")
    progress_bar = st.progress(0)
    if islem_tipi == 'Döndür':
        for i, page in enumerate(doc): 
            page.set_rotation(int(aci))
            progress_bar.progress((i + 1) / len(doc))
    elif islem_tipi == 'Böl':
        if not parametre or parametre.strip() == "":
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zf:
                for i in range(len(doc)):
                    yeni_doc = fitz.open(); yeni_doc.insert_pdf(doc, from_page=i, to_page=i)
                    zf.writestr(f"sayfa_{i+1}.pdf", yeni_doc.write())
                    progress_bar.progress((i + 1) / len(doc))
            return zip_buffer.getvalue(), "zip"
    elif islem_tipi == 'Sayfa Sil':
        sil_no = int(parametre) - 1
        yeni_doc = fitz.open()
        for i in range(len(doc)):
            if i != sil_no: yeni_doc.insert_pdf(doc, from_page=i, to_page=i)
            progress_bar.progress((i + 1) / len(doc))
        doc = yeni_doc
    cikti = io.BytesIO(); doc.save(cikti)
    return cikti.getvalue(), "pdf"

# --- 3. ARAYÜZ ---
if 'page' not in st.session_state: st.session_state.page = 'home'

with st.sidebar:
    st.title("📄 PDF Asistanım")
    if st.button("🏠 Ana Menüye Dön"): st.session_state.page = 'home'; st.rerun()
    st.info("🔒 **Güvenlik:** Dosyalarınız sunucuda tutulmaz.")

if st.session_state.page == 'home':
    st.title("📄 PDF Asistanım")
    st.subheader("Hızlı, Güvenli ve Profesyonel PDF Araçları")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✂️ PDF BÖL"): st.session_state.page = 'Böl'; st.rerun()
        if st.button("🔄 PDF DÖNDÜR"): st.session_state.page = 'Döndür'; st.rerun()
    with col2:
        if st.button("🔗 PDF BİRLEŞTİR"): st.session_state.page = 'Birleştir'; st.rerun()
        if st.button("🗑️ PDF SAYFA SİL"): st.session_state.page = 'Sayfa Sil'; st.rerun()
    if st.button("🪄 PDF DÜZELT (AUTO)"): st.session_state.page = 'Düzelt'; st.rerun()
    if st.button("🖼️ JPG -> PDF (BELGE/KİMLİK)"): st.session_state.page = 'JPG-PDF'; st.rerun()
    st.markdown('<div class="footer-note">🛡️ <b>Gizlilik Notu:</b> İşlem yaptığınız dosyalar oturum sonunda silinir.</div>', unsafe_allow_html=True)

elif st.session_state.page == 'Birleştir':
    st.header("🔗 PDF Birleştirme")
    yuklenen_dosyalar = st.file_uploader("Dosyaları seçin veya sürükleyip bırakın:", type="pdf", accept_multiple_files=True)
    if yuklenen_dosyalar:
        st.write("---")
        with st.container(border=True): 
            st.subheader("📋 Seçilen Dosyalar")
            for i, dosya in enumerate(yuklenen_dosyalar):
                st.markdown(f"**{i+1}.** {dosya.name}")
            st.write("---")
            if st.button("🚀 Birleştir ve İndir"):
                sonuc = pdf_birlestir(yuklenen_dosyalar)
                st.success("PDF'ler birleştirildi!"); st.download_button("📥 İndir", sonuc, "birlesmis_dosya.pdf")

elif st.session_state.page == 'Düzelt':
    st.header("🪄 Akıllı PDF Düzeltme")
    dosya = st.file_uploader("PDF dosyanızı yükleyin:", type="pdf")
    if dosya and st.button("🚀 İşlemi Başlat"):
        sonuc = pdf_duzelt(dosya)
        st.success("Tüm sayfalar düzeltildi!"); st.download_button("📥 İndir", sonuc, "duzeltilmis.pdf")

elif st.session_state.page == 'JPG-PDF':
    st.header("🖼️ JPG'den A4 PDF'e")
    mod = st.radio("Seçim:", ["Tekli Görsel", "Kimlik (Ön/Arka)"])
    i1 = st.file_uploader("Ön Yüz / Görsel:", type=['jpg', 'jpeg', 'png'])
    i2 = st.file_uploader("Arka Yüz:", type=['jpg', 'jpeg', 'png']) if mod == "Kimlik (Ön/Arka)" else None
    if i1 and st.button("🚀 PDF'e Dönüştür"):
        sonuc = jpg_to_a4_pdf(i1, i2)
        st.success("Hazır!"); st.download_button("📥 İndir", sonuc, "belge_cikti.pdf")

else:
    st.header(f"Araç: {st.session_state.page}")
    dosya = st.file_uploader("Dosya Seçin:", type="pdf")
    if dosya:
        if st.session_state.page != "Birleştir": pdf_onizle(dosya)
        param = st.text_input("Sayfa No:") if st.session_state.page in ["Böl", "Sayfa Sil"] else None
        aci = st.selectbox("Açı:", [90, 180, 270, 360]) if st.session_state.page == "Döndür" else 90
        if st.button("🚀 İşlemi Başlat"):
            sonuc, tur = islem_yap(dosya, st.session_state.page, param, aci)
            st.success("İşlem Başarılı!"); st.download_button("📥 İndir", sonuc, f"sonuc.{tur}")