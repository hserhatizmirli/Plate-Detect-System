🚗 Plate-Detect-System (Gerçek Zamanlı Plaka Tanıma)
Bilgisayarınızın veya yerel ağdaki bir cihazın kamerasını kullanarak araç plakalarını gerçek zamanlı olarak tespit eden ve metne dönüştüren web tabanlı bir sistemdir. YOLO11 nesne tespiti ve EasyOCR motorunun gücünü birleştiren bu proje, zorlu çevre koşullarına karşı gelişmiş OpenCV görüntü ön işleme teknikleriyle OCR başarısını maksimize eder.

✨ Temel Özellikler
⚡ Gerçek Zamanlı Tespit: Flask-SocketIO (Eventlet) ile kamera akışından gelen kareler asenkron olarak arka plana iletilir ve anlık olarak işlenir.

🎯 Yüksek Hassasiyet (YOLO11): Sadece %70 güven eşiğini geçen plaka tespitleri işleme alınır. OCR'ın metni daha rahat okuması için plaka bölgesi (ROI) kenarlardan 5'er piksel genişletilir.

🖼️ Gelişmiş Görüntü Ön İşleme: Kırpılan plaka bölgesi gri tonlamaya çevrilir, çözünürlüğü 2 kat büyütülür (CUBIC), CLAHE ile kontrast dengelenir ve morfolojik işlemlerle yazılar pürüzsüzleştirilir.

🧠 Akıllı Karakter Düzeltme: OCR'ın sık yaptığı O ve 0 karışıklığı, Türkiye plaka formatına (İl Kodu + Harf + Rakam) göre Regex ile otomatik onarılır. İl kodunun 01-81 aralığında olup olmadığı denetlenir.

📁 Otomatik Arşivleme: Doğrulanan plakalar; zaman damgası ve plaka adıyla birlikte yerel diskinizdeki Tespitler klasörüne otomatik olarak kaydedilir.

📥 Girdi ve Çıktı (Örnek API Yanıtı)
Sistem kameradan yakalanan hedef kareyi Base64 formatında (/detect endpointi ile) alır ve aşağıdaki gibi yapılandırılmış bir JSON objesi döndürür:

JSON
{ 
  "success": true, 
  "plate_info": { 
    "plate": "34 ABC 123", 
    "yolo_conf": 94.25, 
    "ocr_conf": 91.80, 
    "timestamp": "03.10.2026 - 18.15.30" 
  }, 
  "annotated_image": "base64_kodlanmis_cizgili_gorsel_verisi..." 
}
📂 Proje Yapısı
📄 app.py: Web sunucusunu (Flask), YOLO11 ve EasyOCR modellerini çalıştıran, görüntü işleme ve Regex mantığını barındıran ana arka uç dosyasıdır.

🖥️ templates/index.html: Kamerayı açan, video karelerini arka plana ileten ve plaka geçmişini listeleyen kullanıcı arayüzü.

🧠 best.pt: Proje için özel olarak eğitilmiş YOLO11 plaka tespit ağırlığı.

🖼️ Tespitler/: Başarıyla okunan plakaların görsellerinin arşivlendiği klasör.

🛠️ Kurulum ve Çalıştırma
💡 Not: Sistemin ve OCR motorunun çok daha hızlı çalışması için bilgisayarınızda bir NVIDIA GPU (CUDA) bulunması tavsiye edilir, ancak sistem CPU ile de çalışmaktadır.

1. Depoyu bilgisayarınıza klonlayın ve dizine girin:

Bash
git clone https://github.com/hserhatizmirli/Plate-Detect-System.git 
cd Plate-Detect-System
2. Gerekli Python kütüphanelerini yükleyin:

Bash
pip install flask flask-socketio flask-cors easyocr ultralytics opencv-python numpy polars
3. Dosya yollarını ayarlayın ve uygulamayı başlatın:
(app.py dosyası içindeki MODEL_PATH ve SAVE_DIR yollarını kendi bilgisayarınıza göre düzenlemeyi unutmayın.)

Bash
python app.py
4. Tarayıcınızdan sisteme erişin:
Uygulama başladıktan sonra tarayıcınızdan http://localhost:5000 veya yerel ağ IP'niz üzerinden giriş yapın. Kamera erişim izni istendiğinde onay vererek sistemi kullanmaya başlayabilirsiniz.
