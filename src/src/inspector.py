import os
from PIL import Image
from pypdf import PdfReader
from google import genai
from google.genai import types
from src.schemas import DenetimRaporu


def pdf_metin_cikar(pdf_dosyasi) -> str:
    """Yüklenen SOP PDF dosyasından metin içeriğini çıkarır."""
    okuyucu = PdfReader(pdf_dosyasi)
    metin = []
    for sayfa in okuyucu.pages:
        icerik = sayfa.extract_text()
        if icerik:
            metin.append(icerik)
    return "\n".join(metin)


def gorsel_denetle(gorsel: Image.Image, sop_kurallari: str, api_key: str) -> DenetimRaporu:
    """Görseli verilen SOP (Standart Operasyon Prosedürü) kurallarına göre analiz eder."""
    client = genai.Client(api_key=api_key)

    sistem_talimati = (
        "Sen uzman bir Kalite Kontrol ve Standart Operasyon Prosedürü (SOP) Denetçisisin. "
        "Görevin, sana verilen operasyon kurallarını (SOP) dikkate alarak yüklenen fotoğrafı titizlikle incelemektir. "
        "Fotoğrafta net görünmeyen hiçbir detayı varsayma; görünmüyorsa 'BELİRSİZ' olarak işaretle. "
        "Yanıtlarını tamamen Türkçe ve profesyonel bir dille oluştur."
    )

    kullanici_istemi = f"""
    Aşağıdaki Standart Operasyon Prosedürü (SOP) kurallarına göre ekteki görseli denetle:

    --- STANDART OPERASYON PROSEDÜRÜ (SOP) ---
    {sop_kurallari}
    ------------------------------------------
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[gorsel, kullanici_istemi],
        config=types.GenerateContentConfig(
            system_instruction=sistem_talimati,
            response_mime_type="application/json",
            response_schema=DenetimRaporu,
            temperature=0.1,  # Tutarlı ve nesnel denetim için düşük sıcaklık
        ),
    )

    return DenetimRaporu.model_validate_json(response.text)
