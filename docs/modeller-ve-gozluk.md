# Hazır işaret dili modelleri ve gözlük tasarımı

20 Kasım 2026 itibarıyla proje için üç farklı hedef var. Bir fotoğraftan parmak alfabesi harfi okumak, kısa bir videoda sözlükten tek işaret bulmak ve doğal bir işaret dili cümlesini çevirmek farklı girdi, veri ve ölçüm gerektiriyor.

## Hazır modeller

| Hedef | Hazır seçenek | Bu projede kullanım |
| --- | --- | --- |
| ASL parmak alfabesi | Kamil Rataj’ın indirilebilir MediaPipe modeli 24 statik harf ve işaret yok sınıfı içeriyor. J ve Z hareketle gösteriliyor. | İlk yerel demo bu modeli kullanıyor. A, B ve C ile denendi. [Kaynak ve ağırlıklar](https://github.com/Kamilr616/AI_sign_language_translator/tree/5b2d9a35b8ad2eb008bf5055e0f2959d472d6e40) |
| İzole Türk İşaret Dili (TİD) | SignTurk, kameradan çalıştırmak için 179 sınıflı bir model ve ayrıca 226 sınıflı araştırma ağırlıkları yayımlıyor. Ankara Üniversitesi’nin AUTSL verisi 43 kişinin 226 izole işaretine dayanıyor. | Türkçe bir sonraki demo için 179 sınıflı hazır ağırlığı seçip sınıf listesinden 5–10 yararlı işaretle başlayabiliriz. AUTSL’nin akademik kullanım koşullarını ve seçilen ağırlığın şartlarını yayımdan önce ayrı kontrol etmek gerekiyor. [SignTurk sürümü](https://github.com/ErayKulkizaga/SignTurk/releases/tag/model-assets-v1) · [AUTSL](https://cvml.ankara.edu.tr/datasets/) |
| Sürekli ASL | Google DeepMind’in SL2T modeli Pixel 11’de ASL → İngilizce metin sunuyor. Meta Research’ün SSVP-SLT modeli de ASL → İngilizce için araştırma ağırlıkları sağlıyor. | Google’ın duyurusunda yerel kullanım için indirilebilir ağırlık bulamadım. Meta Research modeli araştırma denemesi için aday. Proje sayfası ticari olmayan kullanım içeren lisans koşullarını belirtiyor. [Google SL2T](https://deepmind.google/blog/putting-sign-language-ai-into-users-hands/) · [SSVP-SLT](https://github.com/facebookresearch/ssvp_slt) |
| Sürekli TİD | BUTID çalışmasının yazarı bir SignT5 ağırlığı yayımlıyor. Ayrı bir çalışma aynı veri kümesinde SHuBERT tabanlı çeviriyi değerlendiriyor. | SignT5 ağırlığı ilk masaüstü denemesi için aday. Kamera karelerinden model girdisini oluşturacak ön işleme kodu doğrulanmadı. [SignT5 ağırlığı](https://huggingface.co/karahansahin/mlp.main.mt5-small.aug.v1) · [BUTID makalesi](https://slrtpworkshop.github.io/assets/papers/SLRTP-18.pdf) · [SHuBERT deneyi](https://aclanthology.org/2026.wslp-1.16/) |

ASL modeliyle TİD ölçümü yapamayız. Örneğin TİD parmak alfabesindeki harflerin çoğu iki elle gösterilir. İzole modelin sözlüğündeki işaretlerin listesi ve doğal cümlelerde işaret sınırlarının bulunması da ayrı sorunlar. [SIGN-HUB TİD dilbilgisi](https://thesignhub.eu/assets/grammar/641/signhub_grammar_tid.pdf) · [SignTurk modeli](https://github.com/ErayKulkizaga/SignTurk)

### Sürekli TİD için ilk kamera denemesi

26 Kasım 2026’da SignT5 ağırlığının `8cbaee5714a6b6bbc834a136e8baa88e74fd46ec` sürümündeki `config.json` ve `safetensors` başlığı kontrol edildi. Model `google/mt5-small` kullanıyor. İlk izdüşüm katmanı her kare için sırası sabit 255 özellik bekliyor. BUTID makalesinin 4.1. bölümü MediaPipe Holistic ile 20 üst beden, 35 yüz ve iki elde 21’er nokta kullanıldığını belirtiyor. Noktaların üçer koordinatı birlikte sayıldığında 291 değer çıkıyor. [Sabit model yapılandırması](https://huggingface.co/karahansahin/mlp.main.mt5-small.aug.v1/blob/8cbaee5714a6b6bbc834a136e8baa88e74fd46ec/config.json) · [Yöntem, bölüm 4.1](https://slrtpworkshop.github.io/assets/papers/SLRTP-18.pdf#page=5)

BUTID’nin 28 Nisan 2025 tarihli kaynak kodu, göz bebeği noktaları çıkarılmış 35 yüz noktasını, iki elin tüm noktalarını ve bulunamayan noktaların sıfırla doldurulmasını gösteriyor. Çıkarılan beden noktalarından eski SignT5 için hangilerinin seçildiği ve model girdisine hangi sırayla dizildiği belirsiz. `dev` dalındaki güncel kod Uni-Sign mimarisini kullanıyor. Mac’te önce Google’ın yayımladığı 6 beden, 37 yüz ve 42 el noktasından oluşan düzen sınanacak. İkinci adayda iki bilek noktası eklenip iki göz bebeği noktası çıkarılarak 8 beden, 35 yüz ve 42 el noktası kullanılacak. [İlk BUTID görüntü işleme kodu](https://github.com/karahan-sahin/BUTID/blob/ac6ace44662f55ebc1dd172bdd0e76f94a8b2f1f/src/run_pose_estimation.py) · [Uni-Sign kaynak kodu](https://github.com/karahan-sahin/BUTID/blob/e6f0207065bab4f6fbfb44ba074a1d82a9ed8681/src/models.py) · [YouTube-ASL, bölüm 4.1](https://proceedings.neurips.cc/paper_files/paper/2023/file/5c61452daca5f0c260e683b317d13a3f-Paper-Datasets_and_Benchmarks.pdf#page=6)

Mac’te ağırlığın iki izdüşüm katmanı yapay girdilerle çalıştırıldı. Ağırlıkta kayıtlı mT5 parametre boyutları ve 250.100 öğelik metin sözlüğü de doğrulandı.

- **İlk canlı diyalog, 00:07–00:37.** Dem Derneği için çekilen tanışma diyaloğunda iki kişi sırayla işaret ediyor. Görüntüye gömülü Türkçe altyazı anlamı kontrol etmek için kullanılabilir. [Türk İşaret Dili – Diyalog 1](https://www.youtube.com/watch?v=ImYKXdtl33E&t=7s)
- **Doğal anlatım, 00:10–00:24.** TİD eğitmeni Hasret Dilsiz Demirtaş’ın +90 röportajından kesit. Bu aralıkta yüz ve iki el önden görünüyor. Görüntüye gömülü Türkçe altyazı var. [Sağır olmak – İşaret dili ana dilim](https://www.youtube.com/watch?v=ai6tcP2TwUY&t=10s)
- **Anlam kontrolü, 47 saniye.** Ankara Üniversitesi TİDYeS’in örnek sorusu, bir TİD metninin Türkçe karşılığını seçmek üzerine. Doğru seçenek videonun sonunda işaretleniyor. [TİD–Türkçe Çeviri – Örnek Soru](https://www.youtube.com/watch?v=hvK_F20BO1I) · [Sınavın içeriği](https://tidyes.ankara.edu.tr/sinavin-icerigi/)

**27 Kasım 2026 Mac testi.** Tam ağırlığın SHA-256 değeri doğrulandı. Mac’te çevrimdışı çalıştırılan SignT5, doğal röportajın 00:10–00:24 ve tanışma diyaloğunun 00:07–00:41 kesitlerini işledi. Altyazıyla daha sıkı karşılaştırma için bu iki videodan altı kısa bölüm de denendi. İki nokta kümesi, iki normalizasyon biçimi ve iki nokta grubu sırası toplam sekiz girdi düzeni oluşturdu. Her düzen gerçek kareler, sırası karıştırılmış kareler ve sıfırlanmış girdilerle çalıştırıldı. Metin üretiminde ağırlığın eğitim ayarlarında kayıtlı beş adaylı arama kullanıldı. Model girdisi yalnızca video karelerinden çıkarılan noktaları içeriyordu.

Sekiz düzenin hiçbirinde altı kısa bölümden doğru bir cümle çıkmadı. Örneğin adın sorulduğu bölümde model “Gel.” veya “Evet.” yazdı. Uzun tanışma kesitinde model bazı çıktılarda “Serdar” adını üretti, ancak bağladığı cümlelerin anlamı diyaloğa uymadı. Sıfır girdide de “Nas...” üretti. Ek kontrolde bir videonun altyazılarına en iyi uyan nokta sırası seçilip diğer videoda denendi. İki yönde de doğru cümle çıkmadı. SignT5’in eğitimde kullandığı tam girdi düzeni hâlâ doğrulanmalı.

Mac testi iPhone’a geçiş koşulunu karşılamadı. Model doğru anlamı düzenli olarak çıkarabildiğinde aynı klip Mac ekranından, 1× hızda ve sesi kapalı oynatılarak uçak modundaki iPhone 15’e gösterilecek. Her anlamlı bölümün bitişi ile metnin ekrana geliş zamanı kaydedilecek.

### Açık verilerle girdi uyarlama denemesi

BUTID’nin yayımladığı test zamanları ve işaretçi kadrajları, yayıncının Türkçe altyazısıyla eşleştirildi. İki yayından üç kesit kullanıldı. Renk kanalı sırası, nokta seçimi, normalizasyon ve bileşen sırası için 480 olası düzen puanlandı. Ayar bir yayından seçilip diğerinde değerlendirildi. Üç kesitte de üretilen cümleler altyazıdaki anlamı karşılamadı. Bu deneme eğitimde kullanılan girdi düzenini doğrulamadı. [BUTID test zamanları](https://github.com/karahan-sahin/BUTID/blob/e6f0207065bab4f6fbfb44ba074a1d82a9ed8681/data/BUTID/legacy/main.test.csv) · [İşaretçi kadrajları](https://github.com/karahan-sahin/BUTID/blob/e6f0207065bab4f6fbfb44ba074a1d82a9ed8681/data/BUTID/legacy/bbox.json)

YouTube-SL-25’in Türk İşaret Dili listesinden elle altyazılı iki eğitim videosu ve farklı bir kanaldan test videosu seçildi. Görünür el noktaları ve altyazı süresi filtreleri eğitimde 16, testte 3 bölüm bıraktı. SignT5’in ağırlıkları sabit tutuldu ve kamera noktalarını dönüştüren küçük bir katman Mac’te 96 adım eğitildi. İlk denemede test altyazısının belirteç başına ortalama çapraz entropi kaybı 13,93’ten 10,67’ye düştü. Üç test bölümünde de anlam yanlış kaldı. Karelerin sırası karıştırıldığında kayıp 10,39 oldu. Bu küçük örnek, uyarlamanın anlam çıkardığını göstermedi. [YouTube-SL-25 kaynak listesi](https://github.com/google-research/google-research/tree/master/youtube_sl_25) · [Eğitim videosu 1](https://www.youtube.com/watch?v=9dfSycw1g1U) · [Eğitim videosu 2](https://www.youtube.com/watch?v=roBUap1sgmM) · [Test videosu](https://www.youtube.com/watch?v=9Vw_ZfWSe8c)

İkinci uyarlama, eğitim sırasında gerçek kare sırasına karıştırılmış sıradan daha yüksek puan vermeyi hedefledi. Test kaybı gerçek sırada 10,29 ve karıştırılmış sırada 10,44 oldu. Eğitim dışında tutulan videoda üç cümleden hiçbiri doğru çevrilmedi. Her iki uyarlama, önceki röportaj ve tanışma kesitlerinde de denendi. İki uzun kesit ve altı kısa bölümün anlamı yakalanamadı. Ağırlıklar ve test verileri yerel çalışma önbelleğinde tutuldu.

### Uçtan uca TİD çevirisi eğitimi

Bakanlığın sözlüğünden Türkçe çevirisi ve işaret sırası açıklaması olan 400 örnek cümle alındı. Türkçe altyazılı TİD videoları eklenerek yerel bir eğitim kümesi hazırlandı. Yeni model 85 el, yüz ve beden noktasının zaman içindeki hareketini Türkçe alt sözcüklere dönüştürüyor. Kaynaklar gruplar halinde ayrıldı. Her çalıştırmada aynı ders videosunun 12 cümlesi ve iki sohbet videosundan toplam altı bölüm testte kullanıldı. [Bakanlığın TİD sözlüğü](https://tidsozluk.aile.gov.tr/) · [Yerel eğitim kodu](../demo/tid/README.md)

İlk model Mac’in MPS aygıtında 192 cümle ile eğitildi. En düşük doğrulama kaybı dördüncü turdaydı. Seçilen ağırlık testteki 18 bölümün tamamında boş çıktı verdi.

İkinci çalıştırma 496 cümleyi kullandı ve doğru video–metin çiftini yanlış eşleşmelerden ayıran ek kayıpla eğitildi. En düşük doğrulama kaybı 23. turdaydı. Ayrı ders videosunda sözcük hata oranı %109,9 ve sohbet bölümlerinde %116,1 oldu. Sohbet kareleri karıştırıldığında oran %161,3’e çıktı. Gerçek videoyla 18 bölümün hiçbirinde doğru çeviri elde edilmedi. WER, eklenen sözcükleri de saydığı için %100’ü geçebilir.

Üçüncü çalıştırma 592 cümleyi kullandı. Bunların 270’inde sözlüğün işaret sırası açıklamaları CTC ile ek eğitim hedefi oldu. En düşük doğrulama kaybı 19. turda görüldü. Ders videosunda WER %172,8, sohbet bölümlerinde %132,3 oldu. Sohbetlerde gerçek ve sırası karıştırılmış kareler aynı WER’yi verdi. İki testte de tam eşleşme sayısı sıfırdı.

Son çalıştırma, üçüncü modelin ağırlığını kullanarak 706 etiketli bölümle eğitildi. Bunların 385’inde işaret sırası açıklaması kullanıldı. Doğrulama kaybı 5,407’den 5,376’ya düştü ve üçüncü tur seçildi. Ders videosunda WER %151,9, sohbet bölümlerinde %216,1 oldu. 18 bölümün hiçbirinde anlamı koruyan bir cümle üretilmedi. Örneğin tanışma diyaloğundaki ad sorma bölümüne bir matematik dersi ifadesiyle yanıt verdi. Bu veri ağırlıklı olarak sözlük cümleleri ve ders videolarından oluşuyor. Sohbet çevirisi ve iPhone’a geçiş koşulu karşılanmadı.

### Hazır ASL cümle çevirisi denemesi

TTIC’nin SHuBERT demosuna Mac’ten iki kendi örneği ve FLEURS-ASL test kümesinden iki yeni video kesiti verildi. FLEURS-ASL klipleri yalnız görüntü içeriyordu. Patlamanın valilik binasının dışında gerçekleştiğini anlatan ilk kesitte bina ve patlama yakalandı, yer bilgisi bozuldu ve ilgisiz sözler eklendi. Islak elle iki kuru tozu top haline getirmeyi anlatan ikinci kesitte ıslak el ayrıntısı yakalandı, fakat toz yerine biber yazıldı ve son işlem kayboldu. İki referans cümlesinin de anlamı korunmadı. Sunucu kuyruğu dahil sonuçlar yaklaşık üç ve beş buçuk dakikada döndü. [SHuBERT demosu](https://huggingface.co/spaces/ShesterG/TTIC-SHuBERT-ASLVideo-to-EnglishText) · [FLEURS-ASL veri kümesi](https://www.kaggle.com/datasets/googleai/fleurs-asl)

Google’ın Pixel 11’deki SL2T modeli FLEURS-ASL’nin SD test bölümünde 70 BLEURT raporluyor. Kamera noktaları telefonda çıkarılıyor, çeviri Google sunucusunda yapılıyor. [Google DeepMind model açıklaması](https://deepmind.google/blog/putting-sign-language-ai-into-users-hands/) · [AISLAC ortak değerlendirme raporu](https://storage.googleapis.com/deepmind-media/DeepMind.com/Blog/putting-sign-language-ai-into-users-hands/aislac-joint-impact-report-for-sl2t-1-0.pdf)

### TİD veri kümesini büyütme

180 BUTID kaynak videosunun zaman kodları Türkçe yayıncı altyazılarıyla eşlendi. 16.186 eğitim, 800 doğrulama ve 1.000 test klibi adayı kaydedildi. Her kaynak video tek bir bölüme ayrıldı. Üç videodan indirilen kısa kesitlerde 14 adayın 12’si mevcut görüntü işleme eşiklerini geçti ve eğitim biçimine dönüştürüldü. İki kaynaktan internet üzerinden okunan 14 aralığın da 11’i eşikleri geçti. Bu kontrol el ve beden noktalarının görünürlüğünü ölçüyor. Yayıncı altyazısıyla işaretin anlam ve zaman uyumu ayrıca incelenecek. Doğal TİD sohbetlerini ölçmek için yayınların dışında bir test kümesi kullanılacak. [BUTID makalesi](https://slrtpworkshop.github.io/assets/papers/SLRTP-18.pdf) · [Veri hazırlama kodu](../demo/tid/README.md#butid-ile-veri-hazırlama)

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
