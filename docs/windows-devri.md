# Windows TİD eğitimi devri

GitHub’dan `main` dalını güncelle, projeyi Windows’ta Codex ile aç ve aşağıdaki metni sohbete yapıştır.

```text
I Saw, I Heard, I Know projesinin TİD cümle çevirisini bu Windows bilgisayarda sürdürüyoruz. Türkçe konuş. AGENTS.md, README.md, docs/windows-devri.md, demo/tid/README.md ve docs/modeller-ve-gozluk.md dosyalarını oku. Bu devirde veri hazırlama ve eğitim Windows’ta yapılacak. iPhone entegrasyonu daha sonra MacBook’ta yapılacak.

Önce yerel Python, işlemci, RAM, disk ve ekran kartını kontrol et. Uyumlu bir NVIDIA kart varsa PyTorch CUDA kur ve küçük bir işlemle GPU’yu doğrula. Windows’ta veri hazırlama, eğitim ve bağımsız ölçümü kendin çalıştır. Uzun işleri disk ve bellek durumuna göre boyutlandır, logları takip et ve tamamlanan kaynakları yeniden işleme.

Mac’te 706 örnekli model, doğal sohbet kesitlerinin anlamını koruyamadı. BUTID’nin 180 videosundan 17.986 yayıncı altyazısı eşleşmesi bulundu. Altyazısı çevresindeki konuşmadan ayrılan klipleri seçen yeni filtre aynı havuzda 6.940 eğitim adayı bıraktı. Bu sayı yalnızca altyazı aralığı kontrolünü kapsıyor. 10 bin eğitim dizisi için Windows’ta kaynak havuzunu büyüt. Altyazıdaki gecikmeyi hesaba kat, işaret hareketi görünmeyen aralıkları ele, eşleşmeleri örneklem üzerinden Türkçe anlam ve zaman bakımından denetle. Eşleşmenin otomatik hizalama ile geldiğini veya insan tarafından kontrol edildiğini kayıtta belirt. Şüpheli klipleri çıkar ve gerekirse yeni aday ekle. Aynı kaynak video yalnız bir bölüme girsin. İşaretçinin kimliği güvenilir biçimde biliniyorsa testte farklı işaretçiler kullan.

Veri hazırlığı tamamlandığında tam 10.000 kullanılabilir eğitim klibiyle Türkçe metin üreten modeli eğit. İlk model için mevcut el, yüz ve beden noktası hattını kullan. Denemeleri ayrı yerel dizinlere kaydet. En iyi ağırlığı doğrulama kümesiyle seç. Ardından eğitimde ve model seçiminde kullanılmamış, Türkçe referansı olan yeni doğal TİD sohbet videolarında ölç. Videodan yalnızca görüntüdeki işaretleri modele ver. Altyazıyı karşılaştırma için kullan. Doğal sohbetlerle BUTID yayın sonuçlarını ayrı kaydet. Referans ile tahminleri, anlam hatalarını, tepki süresini ve WER/CER değerlerini raporla. Boş ve kare sırası karıştırılmış girdilerle karşılaştır.

Sohbetlerde anlam güvenilir biçimde korunursa ağırlığı, belirteç dosyasını ve girdi düzenini Mac’e taşımak için hazırla. Aynı klipleri ekranda 1× hızda, sesi kapalı oynatarak iPhone 15’te uçak modunda canlı kamera testini yapacağız. iPhone’daki A/B/C kamera ve titreşim akışı daha önce doğrulandı.

GitHub işlemlerini Salih elle yapar. Videolar, altyazılar, çıkarılan noktalar ve ağırlıklar .demo-cache altında yerel kalır. Microsoft Teams’e erişme.
```

## Windows’ta çalıştırma

Repo kökünde PowerShell kullan. Python 3.12 x64 ve uyumlu NVIDIA sürücüsü varsa aşağıdaki PyTorch paketi CUDA 12.8 kullanır. Paket seçimini `nvidia-smi` sonucuna ve GPU mimarisine göre yap. Video hazırlamada MediaPipe CPU kullanır. YouTube erişiminde JavaScript çalışma zamanı gerekirse yt-dlp’nin Deno kurulum yönergesini izle. [PyTorch Windows/CUDA paketleri](https://pytorch.org/get-started/previous-versions/#v2110) · [yt-dlp JavaScript kurulumu](https://github.com/yt-dlp/yt-dlp/wiki/EJS)

```powershell
$env:PYTHONUTF8 = '1'
Get-CimInstance Win32_VideoController | Select-Object Name
nvidia-smi
py -3.12 -m venv .venv
$TidPython = '.\.venv\Scripts\python.exe'
& $TidPython -m pip install numpy==1.26.4 opencv-contrib-python==4.11.0.86 mediapipe==0.10.21 beautifulsoup4 sentencepiece safetensors 'yt-dlp[default]'
& $TidPython -m pip install torch==2.11.0 --index-url https://download.pytorch.org/whl/cu128
& $TidPython -c "import torch; assert torch.cuda.is_available(); print(torch.cuda.get_device_name()); print(torch.ones(1, device='cuda'))"
```

Altyazı zamanları ve işaretçi konumları BUTID’nin sabitlenmiş kaynak sürümünden alınır. İlk taramada 500 kaynak dene. Hareket filtresi ve görüntü kalitesi kontrollerinden sonra eğitim bölümü 10 binin altındaysa `--source-limit` değerini artır. Önce birkaç kaynakla deneme yap ve süreye göre `--workers` ayarla. [BUTID hizalama yöntemi, bölüm 3.3](https://slrtpworkshop.github.io/assets/papers/SLRTP-18.pdf#page=4)

```powershell
$TidData = '.demo-cache\tid\butid-windows'
$TidYtDlp = (Resolve-Path '.venv\Scripts\yt-dlp.exe').Path
$ButidIndex = 'https://raw.githubusercontent.com/karahan-sahin/BUTID/e6f0207065bab4f6fbfb44ba074a1d82a9ed8681/data/BUTID/legacy'
New-Item -ItemType Directory -Path $TidData -Force | Out-Null
foreach ($Name in 'main.train.csv', 'main.dev.csv', 'main.test.csv', 'bbox.json') {
    Invoke-WebRequest "$ButidIndex/$Name" -OutFile "$TidData\$Name"
}
& $TidPython demo/tid/align_butid.py $TidData "$TidData\captions" "$TidData\sources.json" --isolated --yt-dlp $TidYtDlp --source-limit 500 --exclude-video OTOYCPFQIuc --exclude-video hxxt8_rohP8 --exclude-video 0kh9YDq5k4I
& $TidPython demo/tid/prepare.py "$TidData\media" "$TidData\features" --sources "$TidData\sources.json" --yt-dlp $TidYtDlp --workers 3
```

`--isolated` en az iki saniyelik altyazılara bakar. Önceki altyazıdan en az 0,5 saniye, sonrakinden en az iki saniye ayırır. Görüntü aralığını tercüman gecikmesi için sona 1,5 saniye ekleyerek okur ve el konumu, hareketi ve görünürlüğüne göre kırpar. Bu kurallar insanın yapacağı anlam denetiminin kapsamını daraltır. Özel olarak seçilmiş test sohbetlerinin `conversation` özelliklerini ayrı video kaynaklarından hazırlayıp aynı özellik dizinine ekle. Referanslar ve zaman aralıkları için `demo/tid/sources.json` biçimini kullan.

```powershell
& $TidPython demo/tid/train.py "$TidData\features" "$TidData\run-10k-01" --device cuda --train-limit 10000
```

Eğitim komutu doğrulama kaybına göre seçilen ağırlığı, belirteç modelini, `metrics.json` ve `predictions.jsonl` dosyalarını çalıştırma dizinine yazar. Sonradan eklenen bağımsız test klipleri için `demo/tid/evaluate.py` kullanılabilir.
