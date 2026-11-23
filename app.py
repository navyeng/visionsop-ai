import os
import json
import streamlit as st
from PIL import Image
from dotenv import load_dotenv
from src.inspector import gorsel_denetle, pdf_metin_cikar

load_dotenv()

st.set_page_config(
    page_title="VisionSOP-AI | Görsel Kalite Kontrol Denetçisi",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 VisionSOP-AI: Çok Modlu Görsel Süreç Denetçisi")
st.markdown(
    "Standart Operasyon Prosedürlerinizi (SOP) yükleyin, saha fotoğrafını ekleyin ve "
    "yapay zekâ destekli otomatik kalite kontrol raporunu saniyeler içinde alın."
)

# Yan Menü: API Anahtarı ve Hazır Senaryolar
with st.sidebar:
    st.header("⚙️ Sistem Ayarları")
    env_key = os.getenv("GEMINI_API_KEY", "")
    api_key = st.text_input(
        "Gemini API Anahtarı",
        value=env_key,
        type="password",
        help="Google AI Studio'dan ücretsiz alabilirsiniz."
    )

    st.divider()
    st.subheader("📋 Örnek Hazır Senaryolar")
    senaryo = st.selectbox(
        "Test için hazır kural seti seçin:",
        [
            "Özel Kural Gir",
            "Kargo Paketleme Kontrolü",
            "Çalışma Masası ve İSG Düzeni",
            "Elektronik Kart / Lehim Ön Kontrolü"
        ]
    )

hazir_kurallar = {
    "Kargo Paketleme Kontrolü": (
        "1. Ürün balonlu naylona (patpat) tamamen sarılmış olmalıdır.\n"
        "2. Kutu içerisinde boşluk kalmaması için dolgu malzemesi kullanılmalıdır.\n"
        "3. Sevk irsaliyesi veya fatura kutunun üst kısmına görünür şekilde yerleştirilmelidir.\n"
        "4. Kutu kapağında ezilme veya yırtık bulunmamalıdır."
    ),
    "Çalışma Masası ve İSG Düzeni": (
        "1. Çalışma yüzeyinde açıkta sıvı içecek bardağı bulunmamalıdır.\n"
        "2. Elektrik kabloları düğümlenmemiş ve güvenli şekilde toplanmış olmalıdır.\n"
        "3. Kesici veya delici el aletleri çalışma alanında açıkta bırakılmamalıdır.\n"
        "4. Aydınlatma çalışma alanını net gösterecek düzeyde olmalıdır."
    ),
    "Elektronik Kart / Lehim Ön Kontrolü": (
        "1. Devre kartı üzerinde yanık, kararma veya sıvı teması izi olmamalıdır.\n"
        "2. Kablo bağlantıları soketlere tam oturmuş olmalıdır.\n"
        "3. Açıkta kalmış, izolasyonu soyulmuş bakır tel bulunmamalıdır."
    )
}

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("1️⃣ Operasyon Kuralları (SOP)")
    yuklenen_pdf = st.file_uploader("SOP Dokümanı Yükle (İsteğe Bağlı PDF)", type=["pdf"])

    varsayilan_metin = ""
    if yuklenen_pdf:
        varsayilan_metin = pdf_metin_cikar(yuklenen_pdf)
        st.success("PDF içeriği başarıyla okundu.")
    elif senaryo in hazir_kurallar:
        varsayilan_metin = hazir_kurallar[senaryo]

    sop_metni = st.text_area(
        "Kontrol Edilecek Kurallar Listesi:",
        value=varsayilan_metin,
        height=200,
        placeholder="Örn: 1. Koruyucu gözlük takılı olmalıdır..."
    )

    st.subheader("2️⃣ Denetlenecek Görsel")
    gorsel_kaynagi = st.radio("Görsel Kaynağı:", ["Dosya Yükle", "Kamerayla Çek"], horizontal=True)

    yuklenen_gorsel = None
    if gorsel_kaynagi == "Dosya Yükle":
        dosya = st.file_uploader("Fotoğraf Seçin (JPG, PNG)", type=["jpg", "jpeg", "png"])
        if dosya:
            yuklenen_gorsel = Image.open(dosya)
    else:
        kamera_dosya = st.camera_input("Fotoğraf Çekin")
        if kamera_dosya:
            yuklenen_gorsel = Image.open(kamera_dosya)

    if yuklenen_gorsel:
        st.image(yuklenen_gorsel, caption="Denetlenecek Saha Görüntüsü", use_container_width=True)

with col2:
    st.subheader("3️⃣ Yapay Zekâ Denetim Raporu")

    if st.button("🚀 Denetimi Başlat", type="primary", use_container_width=True):
        if not api_key:
            st.error("Lütfen sol menüden geçerli bir Gemini API anahtarı girin.")
        elif not sop_metni.strip():
            st.warning("Lütfen kontrol edilecek SOP kurallarını girin veya bir PDF yükleyin.")
        elif yuklenen_gorsel is None:
            st.warning("Lütfen denetlenecek bir fotoğraf yükleyin veya çekin.")
        else:
            with st.spinner("Görsel ve prosedür kuralları analiz ediliyor..."):
                try:
                    rapor = gorsel_denetle(yuklenen_gorsel, sop_metni, api_key)

                    # Durum Rozeti ve Skor
                    m1, m2 = st.columns(2)
                    m1.metric("Genel Karar", rapor.genel_sonuc)
                    m2.metric("Uyumluluk Skoru", f"%{rapor.uyumluluk_skoru}")

                    if rapor.genel_sonuc == "ONAYLANDI":
                        st.success(f"**Özet:** {rapor.ozet_degerlendirme}")
                    elif rapor.genel_sonuc == "REVİZYON GEREKLİ":
                        st.warning(f"**Özet:** {rapor.ozet_degerlendirme}")
                    else:
                        st.error(f"**Özet:** {rapor.ozet_degerlendirme}")

                    st.info(f"🛠️ **Önerilen İlk Aksiyon:** {rapor.aksiyon_onerisi}")

                    st.markdown("#### Madde Bazlı Kontrol Sonuçları")
                    for madde in rapor.detaylar:
                        ikon = "✅" if madde.durum == "UYGUN" else ("❌" if madde.durum == "HATALI" else "⚠️")
                        with st.expander(f"{ikon} {madde.kural_adi} — [{madde.durum}]", expanded=True):
                            st.write(madde.aciklama)

                    # JSON Rapor İndirme Butonu
                    st.download_button(
                        label="📥 Raporu JSON Olarak İndir",
                        data=json.dumps(rapor.model_dump(), ensure_ascii=False, indent=2),
                        file_name="denetim_raporu.json",
                        mime="application/json"
                    )

                except Exception as e:
                    st.error(f"Analiz sırasında bir hata oluştu: {e}")
