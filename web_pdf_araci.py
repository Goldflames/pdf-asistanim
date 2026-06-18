import streamlit as st
import fitz
import io
import zipfile

# --- 1. AYARLAR ---
st.set_page_config(page_title="PDF Asistanım", layout="wide", page_icon="📄")

st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #f1f5f9 !important; }
    [data-testid="stSidebar"] * { color: #1e293b !important; }
    .stApp { background-color: #f8fafc; }
    .stButton>button {
        height: 160px !important; width: 100% !important; border-radius: 20px !important; 
        font-size: 20px !important; font-weight: bold !important;
        background-color: #ffffff !important; color: #1e293b !important; 
        border: 2px solid #e2e8f0 !important; box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stButton>button:hover { border-color: #3b82f6 !important; color: #3b82f6 !important; }
    h1, h2, h3 { color: #1e293b !important; }
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
    st.write("---")
    if st.session_state.page != 'home':
        if st.button("🏠 Ana Menüye Dön"): st.session_state.page = 'home'; st.rerun()

if st.session_state.page == 'home':
    st.title("📄 PDF Asistanım")
    st.subheader("Hızlı, Güvenli ve Profesyonel PDF Araçları")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✂️ PDF BÖL"): st.session_state.page = 'Böl'; st.rerun()
        st.caption("PDF dosyanızı sayfalara ayırın veya spesifik bir sayfayı çekin.")
        if st.button("🔄 DÖNDÜR"): st.session_state.page = 'Döndür'; st.rerun()
        st.caption("Yanlış taranmış PDF sayfalarınızı kolayca çevirin.")
    with col2:
        if st.button("🔗 BİRLEŞTİR"): st.session_state.page = 'Birleştir'; st.rerun()
        st.caption("Birden fazla PDF dosyasını tek bir dosyada birleştirin.")
        if st.button("🗑️ SAYFA SİL"): st.session_state.page = 'Sayfa Sil'; st.rerun()
        st.caption("İstemediğiniz sayfaları PDF'den kalıcı olarak çıkarın.")
else:
    st.header(f"Araç: {st.session_state.page}")
    
    # Dinamik Açıklama
    aciklamalar = {
        "Böl": "Bu araç PDF'inizi sayfalara ayırır. Bir sayfa numarası girerseniz o sayfayı, boş bırakırsanız tüm sayfaları ayrı ayrı (ZIP olarak) indirirsiniz.",
        "Döndür": "Tüm sayfaları seçtiğiniz açıda (90°, 180°, 270°) döndürür ve yeni PDF dosyasını sunar.",
        "Birleştir": "Yüklediğiniz tüm PDF dosyalarını sıralı bir şekilde tek bir dosya haline getirir.",
        "Sayfa Sil": "Belirttiğiniz sayfa numarasını PDF'ten çıkarır ve kalan sayfaları tek PDF olarak sunar."
    }
    st.info(f"💡 **Nasıl Çalışır:** {aciklamalar.get(st.session_state.page, 'İşleminizi seçin.')}")

    with st.expander("📖 Adım Adım Talimatlar"):
        st.write("""
        1. Dosyanızı yükleyin.
        2. Gerekli ayarları (sayfa no veya açı) seçin.
        3. '🚀 İşlemi Başlat' butonuna basın.
        4. İşlem bitince çıkan butondan dosyanızı indirin.
        *Güvenlik Notu: Dosyalarınız sunucuda saklanmaz, işlem bitince otomatik silinir.*
        """)

    dosya = st.file_uploader("PDF dosyanızı yükleyin", type="pdf", accept_multiple_files=(st.session_state.page == "Birleştir"))
    
    if dosya:
        if st.session_state.page != "Birleştir": pdf_onizle(dosya)
        parametre = st.text_input("Sayfa No:") if st.session_state.page in ["Böl", "Sayfa Sil"] else None
        aci = st.selectbox("Açı:", [90, 180, 270, 360]) if st.session_state.page == "Döndür" else 90
        
        if st.button("🚀 İşlemi Başlat"):
            with st.spinner("İşleniyor..."):
                if st.session_state.page == "Birleştir":
                    yazici = fitz.open()
                    for d in dosya: yazici.insert_pdf(fitz.open(stream=d.read(), filetype="pdf"))
                    sonuc = io.BytesIO(); yazici.save(sonuc); sonuc = sonuc.getvalue(); tur = "pdf"
                else: sonuc, tur = islem_yap(dosya, st.session_state.page, parametre, aci)
                
                st.success("İşlem Başarılı!")
                c1, c2 = st.columns(2)
                with c1: st.download_button("📥 İndir", sonuc, f"sonuc.{tur}")
                with c2: 
                    if st.button("🔄 Yeni İşlem"): st.session_state.page = 'home'; st.rerun()