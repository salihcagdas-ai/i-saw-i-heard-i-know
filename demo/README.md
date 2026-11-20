# Fotoğraftan ASL harfi ve Braille

Komut satırı demosu, her fotoğrafta bir statik Amerikan İşaret Dili (ASL) harfi arıyor. Kamil Rataj’ın hazır MediaPipe modeli 24 statik harfi kapsıyor. J ve Z hareket gerektirdiği için kapsam dışında. Sonuç bir harf ve o harfin temel İngilizce Braille hücresi. Kısaltma ve büyük harf işaretleri eklenmiyor. Bu demo hücreyi ekranda gösteriyor. Telefonun titreşimle aktarımı mobil tasarımda tarif ediliyor. [Telefon ve titreşim tasarımı](../docs/modeller-ve-gozluk.md#telefonda-model-ve-titreşimli-braille) · [Model](https://github.com/Kamilr616/AI_sign_language_translator/tree/5b2d9a35b8ad2eb008bf5055e0f2959d472d6e40) · [Birleşik İngilizce Braille kuralları, bölüm 4.1](https://brailleaustralia.org/wp-content/uploads/2025/02/Rules-of-Unified-English-Braille-2024-1.pdf)

## Çalıştırma

Proje kökünde, Windows PowerShell ve Python 3.12 ile. Yerel çalışma alanındaki ortam ve model hazırsa doğrudan aşağıdaki komutla deneyebilirsin.

```powershell
.\.venv\Scripts\python.exe -X utf8 .\demo\asl_braille.py .\demo\examples\A0001_test.jpg .\demo\examples\B0001_test.jpg .\demo\examples\C0001_test.jpg
```

Kendi fotoğrafını denemek için örnek yolların yerine dosya yolunu yaz. Model tek el bekliyor. El bulunmazsa, birden fazla el bulunursa veya sınıf skoru varsayılan 0,75 eşiğinin altındaysa demo Braille üretmiyor. `--min-score` ile eşiği değiştirebilirsin. Model skoru, hatasız tahmin garantisi vermiyor.

## İlk kurulum

Ağırlık, yayımlayanın sabit GitHub sürümünden indirilir ve SHA-256 değeri doğrulanır. Yerel model ve Python ortamı Git dışlama kurallarında. Ağırlık kaynağı GPL-3.0 olarak işaretli. Görüntüler çalıştırma sırasında yerel işlemci üzerinde değerlendirilir. [Ağırlık özeti](https://github.com/Kamilr616/AI_sign_language_translator/blob/5b2d9a35b8ad2eb008bf5055e0f2959d472d6e40/models/SHA256SUMS.txt) · [Kaynak lisansı](https://github.com/Kamilr616/AI_sign_language_translator/tree/5b2d9a35b8ad2eb008bf5055e0f2959d472d6e40)

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r .\demo\requirements.txt
New-Item -ItemType Directory -Force .demo-cache | Out-Null
$modelUri = 'https://raw.githubusercontent.com/Kamilr616/AI_sign_language_translator/5b2d9a35b8ad2eb008bf5055e0f2959d472d6e40/models/gesture_recognizer_asl_0.task'
$tempModel = '.demo-cache/gesture_recognizer_asl_0.task.download'
Invoke-WebRequest -Uri $modelUri -OutFile $tempModel -ErrorAction Stop
if ((Get-FileHash -LiteralPath $tempModel -Algorithm SHA256).Hash -ne '44717cea7089e350dc4fc13a1138c262769a5feccf046d3ff223c427b981fa54') {
    throw 'Model dosyasının SHA-256 değeri eşleşmedi.'
}
Move-Item -LiteralPath $tempModel -Destination '.demo-cache/gesture_recognizer_asl_0.task' -Force -ErrorAction Stop
```

## Test sonuçları

20 Kasım 2026’da Windows ve Python 3.12.10 ile A, B ve C için beşer fotoğraf denendi. Her klasörden dosya sırasıyla 1, 8, 15, 22 ve 30 numaralı örnekler seçildi. Sonuç **13 doğru, 1 yanlış, 1 tahminsiz**. Boş beyaz görüntüde el bulunmadı. İki el içeren sekiz kolajın altısında birden fazla el uyarısı çıktı. Diğer ikisinde model tek el gördü. Bu küçük entegrasyon denemesi yeni kullanıcı, ışık veya gözlük kamerasındaki performansı ölçmüyor. [Dan Rasband’ın CC0 ASL Alphabet Test veri seti](https://www.kaggle.com/datasets/danrasband/asl-alphabet-test)

| Fotoğraf | Beklenen | Sonuç |
| --- | --- | --- |
| `A0001_test.jpg` | A | A → ⠁, %99,6 |
| `B0001_test.jpg` | B | B → ⠃, %99,9 |
| `C0001_test.jpg` | C | C → ⠉, %79,7 |
| `C0008_test.jpg` | C | %46,6, çıktı verilmedi |
| `C0022_test.jpg` | C | D → ⠙, %88,8 |

Tablodaki beş fotoğraf Dan Rasband’ın veri setinden alındı ve `examples` klasöründe bulunuyor. Son iki fotoğrafı aynı komuta ayrı dosya yolları olarak vererek düşük skor ve yüksek skorlu yanlış tahmin davranışını görebilirsin. Harfin, kelimenin ve cümlenin kapsamı ile bir sonraki TİD denemesi araştırma notlarında. [Hazır modeller ve gözlük tasarımı](../docs/modeller-ve-gozluk.md)
