import streamlit as st
import fitz
import io
import zipfile
from PIL import Image

# --- 1. AYARLAR ---
st.set_page_config(page_title="PDF Asistanım", layout="wide", page_icon="📄")

# KESİN GÖRÜNÜRLÜK: NEON KART TASARIMI
st.markdown("""
    <style>
    .stApp, p, h1, h2, h3, .stCaption { color: var(--text-color) !important; }
    div.stButton { text-align: center; margin-bottom: 15px; }
    div.stButton > button {
        background-color: #1a1c24 !important; color: #00f3ff !important;
        border: 2px solid #00f3ff !important; border-radius: 15px !important;
        height: 120px !important; width: 100% !important;
        font-weight: bold !important; font-size: 16px !important;
        box-shadow: 0 0 10px #00f3ff, inset 0 0 5px #00f3ff !important;
        transition: all 0.3s ease-in-out !important;
    }
    div.stButton > button:hover {
        background-color: #00f3ff !important; color: #000000 !important;
        box-shadow: 0 0 30px #00f3ff !important; transform: translateY(-5px) !important;
    }
    .footer-note { padding: 15px; border-radius: 10px; background-color: rgba(0, 243, 255, 0.1); border: 1px solid #00f3ff; text-align: center; }
    [data-testid="stSidebar"] { background-color: var(--secondary-background-color) !important; border-right: 1px solid #00f3ff; }
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

def jpg_to_a4_pdf(img1, img2=None):
    pdf_output = io.BytesIO()
    c = Image.new('RGB', (2480, 3508), 'white')
    p1 = Image.open(img1).convert('RGB')
    p1 = p1.resize((2200, 1500))
    c.paste(p1, (140, 200))
    if img2:
        p2 = Image.open(img2).convert('RGB')
        p2 = p2.resize((2200, 1500))
        c.paste(p2, (140, 1800))
    c.save(pdf_output, "PDF", resolution=100.0)
    return pdf_output.getvalue()

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
    if st.button("🏠 Ana Menüye Dön"): st.session_state.page = 'home'; st.rerun()
    st.info("🔒 **Güvenlik:** Dosyalarınız sunucuda tutulmaz, işlem bitince silinir.")

if st.session_state.page == 'home':
    st.title("📄 PDF Asistanım")
    st.subheader("Hızlı, Güvenli ve Profesyonel PDF Araçları")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("✂️ PDF BÖL"): st.session_state.page = 'Böl'; st.rerun()
        if st.button("🔄 DÖNDÜR"): st.session_state.page = 'Döndür'; st.rerun()
        if st.button("🖼️ JPG -> PDF"): st.session_state.page = 'JPG-PDF'; st.rerun()
    with c2:
        if st.button("🔗 BİRLEŞTİR"): st.session_state.page = 'Birleştir'; st.rerun()
        if st.button("🗑️ SAYFA SİL"): st.session_state.page = 'Sayfa Sil'; st.rerun()
    st.markdown('<div class="footer-note">🛡️ <b>Gizlilik Notu:</b> Yüklediğiniz veriler geçici bellektedir, oturum kapandığında silinir.</div>', unsafe_allow_html=True)

elif st.session_state.page == 'JPG-PDF':
    st.header("🖼️ JPG'den A4 PDF'e")
    mod = st.radio("Belge Tipi:", ["Tekli Görsel", "Kimlik (Ön/Arka Yüz)"])
    i1 = st.file_uploader("Birinci görsel (Ön yüz):", type=['jpg', 'jpeg', 'png'])
    i2 = st.file_uploader("İkinci görsel (Arka yüz):", type=['jpg', 'jpeg', 'png']) if mod == "Kimlik (Ön/Arka Yüz)" else None
    
    if i1 and st.button("🚀 PDF'e Dönüştür"):
        sonuc = jpg_to_a4_pdf(i1, i2)
        st.success("İşlem Başarıyla Tamamlandı!")
        st.download_button("📥 PDF Olarak İndir", sonuc, "belge_cikti.pdf")

else:
    st.header(f"Araç: {st.session_state.page}")
    dosya = st.file_uploader("PDF dosyanızı yükleyin", type="pdf")
    if dosya:
        if st.session_state.page != "Birleştir": pdf_onizle(dosya)
        param = st.text_input("Sayfa No (Bölme/Silme için):") if st.session_state.page in ["Böl", "Sayfa Sil"] else None
        aci = st.selectbox("Döndürme Açısı:", [90, 180, 270, 360]) if st.session_state.page == "Döndür" else 90
        if st.button("🚀 İşlemi Başlat"):
            sonuc, tur = islem_yap(dosya, st.session_state.page, param, aci)
            st.success("İşlem Başarılı!"); st.download_button("📥 İndir", sonuc, f"sonuc.{tur}")