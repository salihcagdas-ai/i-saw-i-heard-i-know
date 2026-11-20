# I Saw, I Heard, I Know

Bu bitirme projesi, işaret dili kullanan bir kişiyle Braille okuyan bir kişinin aynı cihaz üzerinden karşılıklı iletişim kurabilmesini amaçlıyordu. Kameraya gösterilen işaretin yazıya ve Braille’e çevrilmesi, diğer kişinin sesli yanıtının da ekranda yazı olarak gösterilmesi tasarlandı.

Mobil prototipte telefon, kamerasıyla tanınan ve onaylanan işareti titreşimle kodlanmış Braille olarak iletecek. [Telefon ve titreşim tasarımı](docs/modeller-ve-gozluk.md#telefonda-model-ve-titreşimli-braille)

## Yerel demo

Hazır bir model, tek fotoğraftaki Amerikan İşaret Dili (ASL) parmak alfabesi harfini tahmin edip Unicode Braille hücresini gösteriyor. Üç örnek görüntüde A → ⠁, B → ⠃ ve C → ⠉ çıktıları alındı. [Kurulum, örnekler ve test sonuçları](demo/README.md)

iPhone 15 için A, B ve C titreşimlerini oynatan bir Xcode projesi hazırlandı. Gizli harf denemesi hissedilen titreşimi harfle eşleştirmeyi ölçmek için tasarlandı. Gerçek cihaz testi için Xcode’dan yerel kurulum gerekiyor. [iPhone denemesi ve kurulum](ios/README.md)

MacBook’ta geliştirmeye devam ederken mevcut durumu ve ilk cihaz testini devir promptundan açabilirsin. [MacBook devir promptu](docs/macbook-devri.md)

## Projenin geçmişi ve araştırma

Eski arşivden gereksinim raporları, tasarım çizimleri ve tamamlanmamış Python prototipi kurtarıldı. İlk cihaz fikri ve özgün prototipin durumu proje notlarında kayıtlı. [Proje notları](docs/proje-notlari.md)

Araştırma, hazır Türk İşaret Dili modellerini, gözlük ve telefon örneklerini, karşılıklı yanıt kanallarını ele alıyor. [Hazır modeller ve gözlük tasarımı](docs/modeller-ve-gozluk.md)
