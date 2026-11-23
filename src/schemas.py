from pydantic import BaseModel, Field
from typing import List, Literal

class KuralKontrolDetayi(BaseModel):
    kural_adi: str = Field(description="Kontrol edilen standart operasyon kuralının kısa adı")
    durum: Literal["UYGUN", "HATALI", "BELİRSİZ"] = Field(description="Kuralın görüntüdeki durumu")
    aciklama: str = Field(description="Görseldeki kanıtlara dayalı kısa ve net teknik açıklama")

class DenetimRaporu(BaseModel):
    genel_sonuc: Literal["ONAYLANDI", "REVİZYON GEREKLİ", "REDDEDİLDİ"] = Field(
        description="Genel kalite kontrol kararı"
    )
    uyumluluk_skoru: int = Field(
        ge=0, le=100, description="0 ile 100 arasında genel prosedür uyumluluk puanı"
    )
    ozet_degerlendirme: str = Field(
        description="Saha çalışanına yönelik 2-3 cümlelik yapıcı ve net özet geri bildirim"
    )
    detaylar: List[KuralKontrolDetayi] = Field(
        description="Her bir SOP kuralı için ayrı ayrı yapılan görsel analiz sonuçları"
    )
    aksiyon_onerisi: str = Field(
        description="Hata varsa düzeltmek için atılması gereken ilk somut adım"
    )
