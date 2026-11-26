# iPhone 15 prototipi

SwiftUI prototipi A, B ve C’nin Braille hücrelerini iPhone’un titreşim motoruyla oynatır. Diziyi iki kısa darbe başlatır. Ardından gelen altı darbenin kısa olanları boş, uzun olanları kabarık noktayı gösterir. **Kameradan tanı** ekranı, ön kameradaki ASL harfini cihazda tahmin eder. Harf onaylandığında titreşim bir kez oynar. [Telefon tasarımı](../docs/modeller-ve-gozluk.md#telefonda-model-ve-titreşimli-braille) · [Apple Core Haptics](https://developer.apple.com/documentation/corehaptics)

## Modeli hazırlama

Swift Package Manager, MediaPipe Tasks Vision 1.2.3’ün gerekli iOS bileşenlerini Google’dan indirir ve yayımlanan sağlama toplamlarıyla doğrular. İlk derlemeden önce proje kökünde aşağıdaki komutu çalıştır. Fotoğraf demosunun doğrulanmış modeli `.demo-cache` içinde zaten varsa Xcode aynı dosyayı kullanır. Model uygulama paketine kopyalanır ve Git dışında kalır. [Model ve SHA-256 değeri](../demo/README.md#ilk-kurulum) · [MediaPipe 1.2.3 paket kaynağı](https://github.com/google-ai-edge/mediapipe/blob/v1.2.3/Package.swift)

```bash
(
  set -e
  mkdir -p .demo-cache
  model=.demo-cache/gesture_recognizer_asl_0.task
  checksum=44717cea7089e350dc4fc13a1138c262769a5feccf046d3ff223c427b981fa54

  if [ ! -f "$model" ]; then
    download=$(mktemp .demo-cache/asl-model.XXXXXXXX)
    trap 'if [ -f "$download" ]; then rm "$download"; fi' EXIT
    curl --fail --location 'https://raw.githubusercontent.com/Kamilr616/AI_sign_language_translator/5b2d9a35b8ad2eb008bf5055e0f2959d472d6e40/models/gesture_recognizer_asl_0.task' --output "$download"
    printf '%s  %s\n' "$checksum" "$download" | shasum -a 256 -c -
    mv "$download" "$model"
  fi

  printf '%s  %s\n' "$checksum" "$model" | shasum -a 256 -c -
)
```

## iPhone’a yerel kurulum

1. iPhone’un iOS sürümünü destekleyen Xcode’u olan bir Mac’te [BrailleHaptics.xcodeproj](BrailleHaptics.xcodeproj) projesini aç.
2. Xcode’da **BrailleHaptics → Signing & Capabilities → Team** bölümünde kendi Apple hesabının **Personal Team** seçeneğini seç. Yerel kişisel test için ücretsiz hesap kullanılabilir. [Apple kişisel cihazda test kılavuzu](https://developer.apple.com/help/account/basics/about-your-developer-account)
3. iPhone’u USB ile bağla ve Xcode’un hedef listesinden iPhone 15’i seç. Telefon isterse Mac’e güven ve Geliştirici Modu’nu etkinleştir. [Apple Geliştirici Modu kılavuzu](https://developer.apple.com/documentation/xcode/enabling-developer-mode-on-a-device)
4. Xcode’da **Run** düğmesine bas. Kurulumun ardından iPhone’da **Titreşimli Braille** açılır.

Proje iOS 17 ve üzerini hedefler. 26 Kasım 2026’da Xcode 27.2 ile uygulama derlenip iPhone 15’e kuruldu. Salih fiziksel cihazda A, B ve C titreşimlerinin çalıştığını bildirdi. Gizli harf denemesinin sayısal sonucu kaydedilmedi. [Apple’ın fiziksel cihaz notu](https://developer.apple.com/documentation/corehaptics/playing-a-custom-haptic-pattern-from-a-file)

## Çevrimdışı kamera denemesi

1. Uygulama telefona kurulduktan sonra uçak modunu aç ve Wi-Fi’nin kapalı olduğunu kontrol et. **Kameradan tanı → Taramayı başlat** yolunu izle. İlk kullanımda kamera izni ver.
2. Telefonu dik tut. Ön kameraya bir elinle A, B veya C işaretini göster. Üç ardışık karede aynı harfin skoru en az %75 olunca tahmin ekrana gelir.
3. Gerekirse **Onaylanacak harf** alanından doğru harfi seç. **Onayla ve titreştir** düğmesine dokun. Onayladığın harf bir kez titreşir. Kamera taraması tahmin ekrana geldiğinde durur ve **Yeni işaret tara** ile tekrar açılır.
4. Düşük skorda veya sonuç gelmediğinde elini yeniden konumlandır. **Yeniden tara** ile kamerayı baştan dene veya **Elle harf seç** ile doğrudan onay ekranına geç.

## İki dakikalık deneme

1. **A**, **B** ve **C** düğmelerinden her birini bir kez oynat. İki kısa başlangıç darbesini ve ardından gelen altı noktayı hissetmeye çalış.
2. **Gizli harf oynat** düğmesine bas. Titreşim bitince hissettiğin harfi seç. Uygulama doğru harfi ancak seçimden sonra gösterir.
3. Beş gizli denemede doğru sayısını ve en çok karışan harfleri not et. **Tekrar oynat** aynı diziyi yeniden çalar. Noktaları saymak zor gelirse **Yavaş** hızda yeniden dene.

### iPhone’da elle önizleme

iPhone’da **Ayarlar → Ses ve Dokunuş → Zil Sesi → Dokunuş → Yeni Titreşim Yarat** yolundan kısa ve uzun dokunuşları elle kaydedip önizleyebilirsin. A için ilk darbe uzun, B için ilk iki darbe uzun, C için birinci ve dördüncü darbe uzun. Diğer darbeler kısa. Bu önizleme darbe uzunluklarının hissedilip hissedilmediğine dair ilk fikir verir. Uygulamanın kendi zamanlaması Xcode kurulumu sonrası ölçülecek. [Apple özel titreşim kılavuzu](https://support.apple.com/guide/iphone/change-sounds-and-vibrations-iph07c867f28/ios)
