# Bitirme projesinin amacı ve bugünkü durumu

Arşiv incelemesinin ardından hazır bir ASL modeliyle yerel demo eklendi. Eski Python betiği ve ilk arşiv bulguları aşağıda yer alıyor. [Yerel demo ve sonuçlar](../demo/README.md) · [TİD modelleri ve gözlük araştırması](modeller-ve-gozluk.md)

## İlk tasarımdaki konuşma

Proje önerisinde bir kişi kameraya bir işaret gösteriyor. Cihaz, işaretin temsil ettiği metni hareketli noktalarla Braille olarak sunuyor. Karşısındaki kişi sesli yanıt verdiğinde cihaz konuşmayı yazıya döküyor. Öneride iki kişinin kullanabileceği fiziksel bir aygıt tarif edilmiş.

Gereksinim analizinde tasarım akıllı telefona taşınmış. Ana ekran kamera ve mikrofon izni istiyor, çeviriyi gösteriyor ve karşı tarafın yanıtını bekliyor. Arayüz için Flutter ve Dart, görüntü işleme ve tanıma için Python, OpenCV ve TensorFlow düşünülmüş. Raporda ilk dil “English sign” olarak geçiyor. Hangi işaret dilinin ve parmak alfabesinin kastedildiği açık kalmış.

## Arşivin gösterdiği geliştirme düzeyi

| Bileşen | Elde bulunan kanıt |
| --- | --- |
| Tasarım | Doldurulmuş proje önerisi, gereksinim analizinin iki Word sürümü, 15 sayfalık PDF ve beş ayrı görsel. PDF’nin 11–14. sayfaları iletişim akışını ve sistem modellerini gösteriyor. |
| Görüntü işleme | [Python betiği](../prototip/isaretten_braille.py) bir dosyadan görüntü okuyor, 64 × 64 piksele ölçekliyor, griye çeviriyor ve 4.096 sayısal özellik çıkarıyor. |
| İşaret tanıma | Betik A, B ve C etiketleriyle tek komşulu bir sınıflandırıcı kurmayı deniyor. Arşivde etiketli işaret fotoğrafları, eğitilmiş ağırlıklar veya doğruluk ölçümü yok. |
| Braille | Betikte harfler ve Unicode Braille dizileri için iki sözlük var. Hareketli noktaları çalıştıracak donanım şeması, sürücü veya aygıt testi bulunamadı. |
| Mobil uygulama ve konuşma | Raporda ekranlar ve sesli yanıt akışı anlatılıyor. Flutter projesi, mikrofon girişi ve konuşmayı yazıya çeviren kaynak dosya bulunamadı. |

## Python denemesi nerede duruyor?

Özgün betiği `prototip/isaretten_braille.py` adıyla sakladık. Eski `cv.txt` dosyasının içeriği de aynı betikti. Kaynakta üç ayrı sorun var.

1. Örnek çağrı, arşivde karşılığı bulunmayan `path/to/your/sign_image.jpg` yolunu açıyor. Başka bir görüntü seçmek için komut satırı seçeneği yok.
2. Ön işleme her görüntüden 4.096 sayı üretiyor. Sınıflandırıcının eğitim girdisi ise üç Braille dizesinden oluşan tek boyutlu bir dizi. Eğitim bu adımda duruyor.
3. Tanıma başarılı olsa bile çeviriciye bir harf gidecek. Çeviricinin sözlüğü Braille dizileriyle anahtarlanmış. Örneğin `translate_to_braille("A")` çağrısı `Unknown` döndürüyor.

### 20 Kasım 2026 tarihli çalıştırma

Özgün betik ayrı bir yerel ortamda Python 3.12.10, OpenCV 5.1.0, NumPy 2.5.5 ve scikit-learn 1.9.1 ile denendi. `python prototip/isaretten_braille.py` komutuna karşılık gelen varsayılan çalıştırmanın son satırı `Braille Translation: Error in image preprocessing` oldu.

İkinci denemede oluşturulan iki tonlu bir PNG doğrudan betiğin çeviri fonksiyonuna verildi. Ön işleme 0–1 aralığında 4.096 değer üretti. Ardından `knn.fit` çağrısı `ValueError: Expected 2D array, got 1D array instead` hatasıyla durdu. Sözlük fonksiyonu ayrı denendiğinde A, B ve C’nin üçü için de sonuç `Unknown` oldu. Böylece görüntü okuma, sınıflandırma ve karakter dönüşümünün durumu ayrı ayrı doğrulandı.

## Arşiv incelemesinden çıkan kararlar

**Önce eksik kaynağı arayalım.** Bu klasörle birlikte bir Git geçmişi gelmedi. Başka bir diskte, eski bir yedekte veya ayrı bir proje klasöründe `pubspec.yaml`, `lib/main.dart`, bir eğitim defteri, model dosyası ya da etiketli el görüntüleri varsa ilk iş bunları bu arşivle karşılaştırmak olur. RAD’daki GitHub bağlantıları dış projelere verilmiş kaynaklar.

**İlk deneme üç harfe odaklandı.** Hazır ASL modeliyle A, B ve C fotoğraflarından harf ve Braille çıktısı alındı. Sonuçlar demo notlarında fotoğraf etiketleriyle karşılaştırılıyor. [Deneme sonucu](../demo/README.md#test-sonuçları)

**Dokunsal çıktı ayrı bir kabul ölçütü gerektiriyor.** Ekranda Unicode Braille göstermek yazılımın çıktısını incelemeyi sağlar. Bir kullanıcının çıktıyı dokunarak okuyabilmesi için hedef Braille ekranını veya özgün aygıtı seçip gerçek donanımla denemek gerekir. Konuşma ve mobil arayüz sonraki aşamalar olarak ele alınabilir.

## Yayın hazırlığı

Özgün okul belgeleri kişisel bilgiler ve üniversite logosu içeriyor. Eski klasörlerde başka öğrencilerin belgeleri de vardı. Ham akademik arşiv ve ayrıntılı yerel envanter Git dışlama kurallarına alındı. İlk genel sürüm için öneri, bu özetle birlikte çalıştırılabilen örneği, o örneğin test sonucunu ve paylaşım izni belli olan verileri sunmak. Kodun lisansı ve kullanılacak örnek görüntüler ayrıca kararlaştırılmalı.
