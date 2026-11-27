# TİD cümle çevirisi eğitimi

Video karelerinden çıkarılan el, yüz ve beden noktalarıyla Türkçe metin üreten yerel bir araştırma modeli. Eğitimde Bakanlığın sözlüğündeki Türkçe karşılığı verilen örnek cümleler ve zaman kodlu Türkçe altyazısı olan TİD videoları kullanılır. Ses ve görüntüdeki yazı model girdisine girmez. [Güncel Türk İşaret Dili Sözlüğü](https://tidsozluk.aile.gov.tr/) · [YouTube-SL-25 kaynak listesi](https://github.com/google-research/google-research/tree/master/youtube_sl_25)

- `collect_dictionary.py` sözlükte yayımlanan örnek videoları ve Türkçe karşılıklarını yerel önbelleğe alır.
- `prepare.py` örnek cümle veya altyazı aralıklarındaki noktaları çıkarır. 85 noktanın konumu ve görülüp görülmediği bilgisi kullanılır.
- `train.py` Türkçe belirteç sözlüğünü eğitim bölümünden oluşturur, modeli eğitir ve en düşük doğrulama kaybına sahip ağırlığı kaydeder.

## Yerel çalıştırma

Proje kökünde Python 3.11, MediaPipe 0.10.21, NumPy 1.x, OpenCV, Beautiful Soup, PyTorch, SentencePiece ve safetensors kullanılır. Altyazılı video dizini, [sources.json](sources.json) içindeki kimliklerle `<id>.mp4` ve `<id>.tr.json3` dosyalarını içerir. JSON3 dosyaları YouTube’un yayımladığı zaman kodlu Türkçe altyazılardır. Sohbet kliplerinin zamanları `sources.json` içinde kayıtlıdır.

```sh
root=.demo-cache/tid/training
python demo/tid/collect_dictionary.py "$root/dictionary" --limit 400 --pages 2
python demo/tid/prepare.py "$root/dictionary" "$root/features" --dictionary
python demo/tid/prepare.py "$root/sources" "$root/features" --sources demo/tid/sources.json
python demo/tid/train.py "$root/features" "$root/run-01" --device mps
```

PyTorch’ta MPS kullanılamıyorsa `--device cpu` seçilebilir. Hazırlanan noktalar, videolar, tahminler ve ağırlıklar önbellekte kalır.

Windows’ta NVIDIA kartla eğitimde `--device cuda` kullanılabilir. [Windows kurulumu ve 10 bin kliplik eğitim](../../docs/windows-devri.md)

Sözlükteki işaret sırası açıklamalarını eğitimde ek hedef olarak kullanmak için `collect_dictionary.py "$root/dictionary" --glosses` çalıştırılır ve eğitime `--glosses "$root/dictionary/glosses.json"` verilir. `--contrastive 0.45`, doğru video ve altyazı eşleşmesini aynı gruptaki yanlış eşleşmelerden ayıran ek eğitim kaybını açar.

## BUTID ile veri hazırlama

`align_butid.py`, BUTID’nin tek altyazılı klip listesindeki başlangıç ve bitiş zamanlarını yayıncının Türkçe altyazısına en fazla 80 ms farkla eşler. Birden çok olası altyazısı olan aralıklar ve geçersiz görüntü kırpma kayıtları elenir. Çıktıda kaynak adresi, işaretçinin görüntüdeki alanı ve her klibin zamanı ile Türkçe altyazısı yer alır. Eğitim, doğrulama ve test bölümlerinden her kaynak video yalnızca birine atanır. [BUTID makalesi](https://slrtpworkshop.github.io/assets/papers/SLRTP-18.pdf) · [Kullanılan kaynak listesi](https://github.com/karahan-sahin/BUTID/tree/e6f0207065bab4f6fbfb44ba074a1d82a9ed8681/data/BUTID/legacy)

`index` dizini `main.train.csv`, `main.dev.csv`, `main.test.csv` ve `bbox.json` dosyalarını içerir. Türkçe altyazılar `<id>.tr.json3` adıyla önbelleğe alınır. Üç kaynak önceki model denemelerinde kullanıldığı için örnek komutta dışarıda tutulur.

```sh
root=.demo-cache/tid/butid-pilot
python demo/tid/align_butid.py "$root" "$root/captions" "$root/sources.json" \
  --yt-dlp yt-dlp --source-limit 180 --max-clips-per-source 100 \
  --exclude-video OTOYCPFQIuc --exclude-video hxxt8_rohP8 --exclude-video 0kh9YDq5k4I
```

Manifestteki zamanlar orijinal videoya göredir. `prepare.py` varsa `<id>.mp4` dosyasını kullanır. `--yt-dlp` ile eksik kaynakların etiketli aralıklarını internetten okur ve yalnızca çıkarılan noktaları kaydeder. Yeniden çalıştırıldığında tamamlanmış kaynakları atlar.

```sh
python demo/tid/prepare.py "$root/media" "$root/features" --sources "$root/sources.json" \
  --split train --yt-dlp yt-dlp
```

Yalnızca kısa bir bölüm yerel dosya olarak indirilirse bölümün başlangıç zamanı etiket zamanlarından çıkarılır. Yayın altyazısı ile işaret arasında tercümanın gecikmesi olabilir. Eğitim ve ölçüm öncesinde örnekler bu açıdan kontrol edilir. Cümle sayımı her klip için bir kez yapılır. Fotoğraflar ve video kareleri el şekli tanımaya ek veri sağlayabilir.

## Ölçüm

Kaynak grupları eğitim ve test bölümleri arasında ayrılır. Model seçimi doğrulama videosuyla yapılır. Son ölçüm ayrı bir ders videosunda ve iki sohbet kaydının kısa bölümlerinde yapılır. `metrics.json` dosyasında sözcük hata oranı (WER), karakter hata oranı (CER) ve tam eşleşme yer alır. Girdi sırası karıştırıldığında ve boş girdi verildiğinde aynı ölçümler tekrarlanır.

WER altyazının sözcüklerine göre hesaplanır. Farklı sözlerle doğru anlam veren bir cümle de bu ölçümde hata sayılabilir. Canlı iPhone denemesinden önce ayrı sohbetlerde anlamın korunması gerekir. [Projenin TİD testleri](../../docs/modeller-ve-gozluk.md)
