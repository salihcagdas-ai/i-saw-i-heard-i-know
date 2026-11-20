# Hazır işaret dili modelleri ve gözlük tasarımı

20 Kasım 2026 itibarıyla proje için üç farklı hedef var. Bir fotoğraftan parmak alfabesi harfi okumak, kısa bir videoda sözlükten tek işaret bulmak ve doğal bir işaret dili cümlesini çevirmek farklı girdi, veri ve ölçüm gerektiriyor.

## Hazır modeller

| Hedef | Hazır seçenek | Bu projede kullanım |
| --- | --- | --- |
| ASL parmak alfabesi | Kamil Rataj’ın indirilebilir MediaPipe modeli 24 statik harf ve işaret yok sınıfı içeriyor. J ve Z hareketle gösteriliyor. | İlk yerel demo bu modeli kullanıyor. A, B ve C ile denendi. [Kaynak ve ağırlıklar](https://github.com/Kamilr616/AI_sign_language_translator/tree/5b2d9a35b8ad2eb008bf5055e0f2959d472d6e40) |
| İzole Türk İşaret Dili (TİD) | SignTurk, kameradan çalıştırmak için 179 sınıflı bir model ve ayrıca 226 sınıflı araştırma ağırlıkları yayımlıyor. Ankara Üniversitesi’nin AUTSL verisi 43 kişinin 226 izole işaretine dayanıyor. | Türkçe bir sonraki demo için 179 sınıflı hazır ağırlığı seçip sınıf listesinden 5–10 yararlı işaretle başlayabiliriz. AUTSL’nin akademik kullanım koşullarını ve seçilen ağırlığın şartlarını yayımdan önce ayrı kontrol etmek gerekiyor. [SignTurk sürümü](https://github.com/ErayKulkizaga/SignTurk/releases/tag/model-assets-v1) · [AUTSL](https://cvml.ankara.edu.tr/datasets/) |
| Sürekli ASL | Google DeepMind’in SL2T modeli Pixel 11’de ASL → İngilizce metin sunuyor. Meta Research’ün SSVP-SLT modeli de ASL → İngilizce için araştırma ağırlıkları sağlıyor. | Google’ın duyurusunda yerel kullanım için indirilebilir ağırlık bulamadım. Meta Research modeli araştırma denemesi için aday. Proje sayfası ticari olmayan kullanım içeren lisans koşullarını belirtiyor. [Google SL2T](https://deepmind.google/blog/putting-sign-language-ai-into-users-hands/) · [SSVP-SLT](https://github.com/facebookresearch/ssvp_slt) |
| Sürekli TİD | BUTID üzerinde SHuBERT tabanlı bir çeviri çalışması yayımlandı. | Bu incelemede açıkça indirip yerelde çalıştırabildiğimiz genel amaçlı bir TİD cümle modeli doğrulanamadı. Sürekli çeviriye geçilecekse video verisine erişim ve bir başlangıç modelinin uyarlanması ayrı iş kalemleri. [BUTID araştırması](https://aclanthology.org/2026.wslp-1.16/) |

ASL modeliyle TİD ölçümü yapamayız. Örneğin TİD parmak alfabesindeki harflerin çoğu iki elle gösterilir. İzole modelin sözlüğündeki işaretlerin listesi ve doğal cümlelerde işaret sınırlarının bulunması da ayrı sorunlar. [SIGN-HUB TİD dilbilgisi](https://thesignhub.eu/assets/grammar/641/signhub_grammar_tid.pdf) · [SignTurk modeli](https://github.com/ErayKulkizaga/SignTurk)

## Piyasada ve araştırmada benzerleri

| Sistem | Gösterdiği işlev |
| --- | --- |
| Meta Ray-Ban Display | Dışa bakan kamera, mikrofon, açık kulak hoparlörleri ve gözlüğü takanın gördüğü lens içi ekran. Konuşma altyazısı ve canlı yabancı dil çevirisi belgelenmiş. Meta’nın destek açıklamalarında yerleşik işaret dili çevirisi bulamadım. Standart Ray-Ban Meta modellerinde lens ekranı yok. [Display donanımı](https://about.fb.com/news/2025/09/meta-ray-ban-display-ai-glasses-emg-wristband/) · [Canlı çeviri](https://www.meta.com/help/ai-glasses/955732293123641/) · [Model karşılaştırması](https://www.meta.com/ai-glasses/compare/) |
| Even G2 | Lens ekranı ve mikrofonu olan, kamerayı ve hoparlörü gözlüğe koymayan ürün. Konuşma çevirisini yazıyla gösterebiliyor. Alıcıya sesli yanıt için telefon gibi ikinci bir cihaz gerekir. [Donanım](https://hub.evenrealities.com/docs/getting-started/overview) · [Çeviri](https://www.evenrealities.com/en-GB/blogs/buyers-guide/ai-translation-glasses) |
| Google Pixel 11 | Live Transcribe, ASL’yi İngilizce metne çeviriyor. Kullanıcı telefonda metni onaylayıp büyütebiliyor veya muhatabına sesli okutabiliyor. Telefon ön kamerası el ve yüzü görüyor. [Kullanım kılavuzu](https://support.google.com/pixelphone/answer/9158064?hl=en) · [Model açıklaması](https://deepmind.google/blog/putting-sign-language-ai-into-users-hands/) |
| SignGlass, 2025 | Gözlüğü işaret eden kişinin taktığı araştırma prototipi. Üç geniş açılı kamerayla kendi ellerini ve yüzünü yakalıyor. 14 Sağır katılımcıyla değerlendirildi. [ACM yayını](https://doi.org/10.1145/3746059.3747782) |
| Asistan Gözlük, 2019 | Türkiye’de konuşmayı yazıya ve işareti yazı/sese aktarmayı hedefleyen öğrenci prototipi. [Fatih İlçe Millî Eğitim](https://fatih.meb.gov.tr/www/asistan-gozluk-projesi/icerik/486) |
| İşaret dili–Braille arayüzü, 2017 | İşaretten Braille’e gerçek zamanlı dönüşüm daha önce IEEE’de yayımlanmış bir araştırma konusu. [Yayın kaydı](https://doi.org/10.1109/CSNT.2017.8418569) |
| Orbit Chat | Android telefon ve Bluetooth Braille ekranıyla karşılıklı yazışma. Braille okuyan kişi fiziksel hücrelerden okuyup Braille klavyesinden yanıt verebiliyor. [Orbit Chat kılavuzu](https://www.orbitresearch.com/support/orbit-chat-support/) |

## Karşılıklı iletişimde nerede kopabilir?

| Durum | İlk prototipte çözüm |
| --- | --- |
| Altyazıyı yalnız gözlüğü takan kişi görüyor. Açık kulak hoparlörü onun kulağına yöneliyor. | Onaylanan yanıtı muhataba telefonda büyük yazıyla göster veya telefon hoparlöründen okut. Hangi çıkışın kullanılacağını başta seçtir. |
| İşaret eden kişi gözlüğü takıyor. Öne bakan kamera kendi yüzünü göremiyor ve el kadrajı başla birlikte oynuyor. | İlk sürümde telefonu standa koy. Kamera yüzü, üst bedeni ve iki eli birlikte görsün. Gözlüğü daha sonra gelen altyazının isteğe bağlı ekranı olarak dene. |
| Alıcı ekrandaki karakteri göremiyor ve sesi kullanamayabilir. | Telefonun titreşim motoruyla Braille nokta dizisini oynat. Kabartmalı hücreyle okumayı tercih edenler için bağlı Braille ekranı kullan. Yanıtı Braille klavyesiyle de al. [Android Braille ekranları](https://support.google.com/accessibility/android/answer/3535226) · [AADB iletişim yöntemleri](https://www.aadb.org/factsheets/db_communications.html) |
| Sistem yanlış işareti yüksek skorla tanıyabiliyor veya mimikle verilen soru ve olumsuzluğu kaçırabiliyor. | Yanıtı göndermeden ya da seslendirmeden önce düzenlenebilir bir taslak göster. Emin olunmayan durumda yeniden işaretleme ve klavye seçenekleri sun. [SL2T ortak etki raporu](https://storage.googleapis.com/deepmind-media/DeepMind.com/Blog/putting-sign-language-ai-into-users-hands/aislac-joint-impact-report-for-sl2t-1-0.pdf) |
| Telefon kendi okuduğu yanıtı mikrofondan yeniden duyuyor. | İlk konuşma demosunda sıra tabanlı ilerle. Sesli okuma sırasında konuşma tanımayı durdur. |

## Telefonda model ve titreşimli Braille

Mobil prototipin akışı **kamera → cihazda işaret tanıma → onaylanmış metin → Braille hücreleri → telefon titreşimi**. Telefon mesajın başında ayırt edilebilir bir başlangıç örüntüsü, ardından her Braille hücresinin nokta dizisini oynatacak. İlk testte alıcı telefonu tutarak veya sabitlenmiş telefonun gövdesine dokunarak titreşimi hissedecek. Uygulama işareti önce yakalayacak. Titreşim sırasında sarsılan kareleri ve aynı işareti yeniden işlememek için tanımayı bekletecek.

### Titreşimle nokta aktarımı

Tek titreşim motoru, hücredeki altı noktanın konumunu zaman sırasıyla iletebilir. İlk denemede her nokta için eşit süreli bir sıra kullanabiliriz. Kısa darbe boş noktayı, uzun darbe kabarık noktayı temsil eder. Başlangıç örüntüsü ve harfler arası boşluk, dizinin neresinde olunduğunu belirtir.

| Harf | Braille noktaları | Önerilen altı darbenin sırası |
| --- | --- | --- |
| A | 1 | Uzun, kısa, kısa, kısa, kısa, kısa |
| B | 1, 2 | Uzun, uzun, kısa, kısa, kısa, kısa |
| C | 1, 4 | Uzun, kısa, kısa, uzun, kısa, kısa |

Android uygulaması bu süreleri `VibrationEffect.createWaveform` ile titreşim motoruna iletebilir. iOS karşılığı desteklenen donanımda Core Haptics. Titreşim süreleri ve harf araları bir deneme ayarı. Braille okurlarıyla harfleri ekrana bakmadan ayırt etme oranı, okuma süresi ve tekrar ihtiyacı ölçülmeli. Tekrar oynatma ve hız ayarı ilk testte yer almalı. Altı noktalı Braille’i telefonun kısa ve uzun titreşimlerine kodlayan bir araştırma emsali var. [Android titreşim örüntüleri](https://developer.android.com/reference/android/os/VibrationEffect) · [Apple Core Haptics](https://developer.apple.com/documentation/corehaptics) · [Titreşimle Braille araştırması](https://doi.org/10.1093/iwc/iwt017)

ASL demosu tek harf döndürüyor. Bir TİD işareti Türkçe bir sözcüğe eşlendiğinde uygulama sözcüğü Türkçe Braille hücrelerine çevirecek. Türkçe harfleri, sayıları ve işaretleri işlerken masaüstündeki İngilizce harf eşlemesi yerine Türkçe Braille tablosu kullanılacak. [Liblouis Türkçe Braille tablosu](https://github.com/liblouis/liblouis/blob/master/tables/tr-g1.ctb)

### Modeller nasıl çalıştırılacak?

- **ASL harf demosu.** Android’de kamera kareleri CameraX’ten alınır ve uygulamanın yerel `.task` modeline MediaPipe Gesture Recognizer ile iletilir. Google’ın mobil kütüphanesi bu model biçimini ve canlı kamera modunu destekliyor. Bir işaret birkaç kare boyunca tutuyorsa uygulama tek bir aday gösterir. Aynı işareti her karede tekrar oynatmaz. Şu an doğrulanan çalıştırma Windows’ta fotoğraf girdisiyle yapıldı. [MediaPipe Gesture Recognizer](https://developers.google.com/edge/mediapipe/solutions/vision/gesture_recognizer)
- **SignTurk ile TİD.** Modelin yayımlanan 179 sınıflı sürümü bir `.keras` dosyası. Uygulama 16 kareden iki elin noktalarını çıkaracak ve zaman sırasıyla, masaüstündeki normalizasyonu koruyarak modele `1 × 16 × 156` biçiminde verecek. Hazır ağırlığı yeniden eğitmeden LiteRT için `.tflite` biçimine dönüştürmek ilk aday. Dönüşümden sonra aynı kliplerde masaüstü ve mobil tahminleri karşılaştırılacak. Ön kameranın sol–sağ düzeni ve karelerin hangi aralıkla seçildiği de bu karşılaştırmada kontrol edilecek. Bu ağırlığın dönüşümü ve gerçek telefondaki hızı henüz ölçülmedi. [SignTurk ağırlık listesi](https://github.com/ErayKulkizaga/SignTurk/blob/main/model-assets.json) · [SignTurk giriş hazırlığı](https://github.com/ErayKulkizaga/SignTurk/blob/main/live_pipeline.py) · [LiteRT LSTM dönüşümü](https://developers.google.com/edge/litert/conversion/tensorflow/rnn)

Model dosyası ve Braille tablosu telefona yüklendikten sonra bu kamera, tanıma ve titreşim hattı çevrimdışı çalışacak şekilde tasarlanıyor. İlk test cihazı iPhone 15 olarak belirlendi. iOS için önce A, B ve C’nin titreşimden ayırt edilmesini deneyen Core Haptics prototipi hazırlandı. Canlı kamera aşamasında mevcut ASL `.task` dosyası AVFoundation üzerinden alınan karelerle MediaPipe’ın iOS kütüphanesine verilecek. [iPhone denemesi](../ios/README.md) · [MediaPipe iOS desteği](https://developers.google.com/edge/mediapipe/solutions/vision/gesture_recognizer)

## İlk saha denemesi

**Telefonu ortak iletişim cihazı olarak kullan.** Masada duran telefon bir kişinin onayladığı TİD işaretini titreşimli Braille, büyük yazı veya sesle muhatabına iletsin. Karşı tarafın konuşma ya da yazı yanıtı aynı sohbette görünsün. Her iki yön de klavyeyle düzeltilebilsin. Sağır TİD kullanıcıları ve Braille kullanan katılımcılarla hangi girdilerin ve çıktının işe yaradığını birlikte değerlendirelim. [WFD erişilebilirlik yaklaşımı](https://wfdeaf.org/resources/accessibility/)

İlk senaryoyu tek bir kısa konuşma etrafında ölçebiliriz. Örneğin iki kişi bir buluşma yerini doğrulasın. Daha önce eğitimde görülmemiş katılımcılarda yanlış tahmin, hiç sonuç dönmeyen deneme, düzeltme sayısı ve yanıtın karşı tarafa ulaşma süresini ayrı kaydedelim. TİD işaret sözlüğüyle titreşimli okumanın bu akıştaki performansı gözlük donanımı seçimine yön verebilir.
