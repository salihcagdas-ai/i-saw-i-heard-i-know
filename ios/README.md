# iPhone 15 titreşim denemesi

Bu SwiftUI prototipi, A, B ve C harflerinin altı Braille noktasını iPhone’un titreşim motoruyla oynatmak için hazırlandı. İki kısa darbe diziyi başlatıyor. Ardından sabit aralıklarla altı darbe geliyor. Kısa darbe boş noktayı, uzun darbe kabarık noktayı temsil ediyor. Bu adım titreşim dizilerini tanımayı ölçüyor. Kameradan işaret tanıma bir sonraki aşama. [Telefon tasarımı](../docs/modeller-ve-gozluk.md#telefonda-model-ve-titreşimli-braille) · [Apple Core Haptics](https://developer.apple.com/documentation/corehaptics)

## iPhone’a yerel kurulum

1. iPhone’un iOS sürümünü destekleyen Xcode’u olan bir Mac’te [BrailleHaptics.xcodeproj](BrailleHaptics.xcodeproj) projesini aç.
2. Xcode’da **BrailleHaptics → Signing & Capabilities → Team** bölümünde kendi Apple hesabının **Personal Team** seçeneğini seç. Yerel kişisel test için ücretsiz hesap kullanılabilir. [Apple kişisel cihazda test kılavuzu](https://developer.apple.com/help/account/basics/about-your-developer-account)
3. iPhone’u USB ile bağla ve Xcode’un hedef listesinden iPhone 15’i seç. Telefon isterse Mac’e güven ve Geliştirici Modu’nu etkinleştir. [Apple Geliştirici Modu kılavuzu](https://developer.apple.com/documentation/xcode/enabling-developer-mode-on-a-device)
4. Xcode’da **Run** düğmesine bas. Kurulumun ardından iPhone’da **Titreşimli Braille** açılır.

Proje iOS 17 ve üzerini hedefliyor. Gerçek titreşimi değerlendirmek için fiziksel iPhone gerekiyor. Windows’ta Swift dosyalarının sözdizimi ve Xcode proje referansları kontrol edildi. iOS derlemesi, imzalama ve titreşim kalitesi henüz gerçek donanımda doğrulanmadı. [Apple’ın fiziksel cihaz notu](https://developer.apple.com/documentation/corehaptics/playing-a-custom-haptic-pattern-from-a-file)

## İki dakikalık deneme

1. **A**, **B** ve **C** düğmelerinden her birini bir kez oynat. İki kısa başlangıç darbesini ve ardından gelen altı noktayı hissetmeye çalış.
2. **Gizli harf oynat** düğmesine bas. Titreşim bitince hissettiğin harfi seç. Uygulama doğru harfi ancak seçimden sonra gösterir.
3. Beş gizli denemede doğru sayısını ve en çok karışan harfleri not et. **Tekrar oynat** aynı diziyi yeniden çalar. Noktaları saymak zor gelirse **Yavaş** hızda yeniden dene.

### iPhone’da elle önizleme

iPhone’da **Ayarlar → Ses ve Dokunuş → Zil Sesi → Dokunuş → Yeni Titreşim Yarat** yolundan kısa ve uzun dokunuşları elle kaydedip önizleyebilirsin. A için ilk darbe uzun, B için ilk iki darbe uzun, C için birinci ve dördüncü darbe uzun. Diğer darbeler kısa. Bu önizleme darbe uzunluklarının hissedilip hissedilmediğine dair ilk fikir verir. Uygulamanın kendi zamanlaması Xcode kurulumu sonrası ölçülecek. [Apple özel titreşim kılavuzu](https://support.apple.com/guide/iphone/change-sounds-and-vibrations-iph07c867f28/ios)
