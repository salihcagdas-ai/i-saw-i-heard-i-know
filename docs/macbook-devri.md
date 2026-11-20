# MacBook devir promptu

GitHub’dan klonlanan proje klasörünü Codex’te aç ve aşağıdaki metni yeni chate yapıştır. Mevcut Xcode projesi `ios/BrailleHaptics.xcodeproj` altında.

```text
I Saw, I Heard, I Know bitirme projemi bu MacBook’ta devam ettiriyoruz. Test cihazım iPhone 15. Benimle Türkçe konuş ve önce AGENTS.md, README.md, ios/README.md, demo/README.md ile docs/modeller-ve-gozluk.md dosyalarını oku.

Hedefimiz telefonun kamerasıyla tanınan işareti yazıya çevirmek ve Braille hücrelerini telefonun kendi titreşim motoruyla iletmek. Her hücreden önce iki kısa başlangıç darbesi var. Altı nokta zaman sırasıyla oynatılıyor. Kısa darbe boş, uzun darbe kabarık noktayı temsil ediyor. Kullanıcı mesajı düzeltip onaylayabilmeli. Titreşim oynarken kamera tanıması beklemeli.

Mevcut durum
- Windows’ta hazır MediaPipe ASL modeliyle A, B ve C fotoğraflarından Braille çıktısı alındı. 15 fotoğrafta 13 doğru, 1 yanlış, 1 sonuçsuz tahmin var. Modelin sabit indirme bağlantısı ve SHA-256 değeri demo/README.md içinde. Model ağırlığı yerel olarak indirilir.
- ios/BrailleHaptics.xcodeproj mevcut. A, B ve C titreşimlerini oynatan SwiftUI ve Core Haptics denemesinde hız ayarı, tekrar, durdurma ve gizli harf testi var. Windows’ta sözdizimi, proje referansları ve örüntü zamanlamaları kontrol edildi. Mac’te iOS derlemesi ve iPhone’da titreşim henüz doğrulanmadı.

Önce mevcut Xcode projesini Mac’te derle. Yerel derleme sorunlarını çöz. Personal Team seçme, bilgisayara güvenme veya Geliştirici Modu gibi telefon ve hesap adımlarında bana gereken işlemi söyle. iPhone 15’te A/B/C, gizli harf, hız, tekrar ve durdurmayı deneyip sonucu kaydedelim.

Titreşim testi doğrulandıktan sonra aynı iOS projesine AVFoundation kamera akışını ve mevcut ASL .task modelini MediaPipe’ın iOS kütüphanesiyle ekle. İlk kabul testi iPhone 15’te çevrimdışı A/B/C tanıma, kullanıcı onayı ve tek seferlik doğru titreşim. Yanlış veya düşük skorlu tahminlerde düzeltme ya da yeniden deneme yolu olsun. TİD için SignTurk mobil dönüşümüne bu aşamadan sonra geçelim.

GitHub ve diğer uzak sistemlere yazma ya da yayın komutu çalıştırma. Yerel değişiklikleri ve testleri tamamla. Gerektiğinde yerel commit hazırla ve bana repo, dal, SHA ile elle çalıştıracağım push komutunu ver.
```
