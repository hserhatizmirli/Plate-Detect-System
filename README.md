=============================================
  ██████╗ ██╗      █████╗ ████████╗███████╗    ██████╗ ███████╗████████╗
  ██╔══██╗██║     ██╔══██╗╚══██╔══╝██╔════╝    ██╔══██╗██╔════╝╚══██╔══╝
  ██████╔╝██║     ███████║   ██║   █████╗      ██║  ██║█████╗     ██║   
  ██╔═══╝ ██║     ██╔══██║   ██║   ██╔══╝      ██║  ██║██╔══╝     ██║   
  ██║     ███████╗██║  ██║   ██║   ███████╗    ██████╔╝███████╗   ██║   
  ╚═╝     ╚══════╝╚═╝  ╚═╝   ╚═╝   ╚══════╝    ╚═════╝ ╚══════╝   ╚═╝   
=============================================
           PLATE-DETECT-SYSTEM - GERÇEK ZAMANLI PLAKA TANIMA (ALPR)
================================================================================

[ PROJE GENEL BAKIŞI ]
Bilgisayarınızın veya yerel ağdaki bir cihazın kamerasını kullanarak araç 
plakalarını gerçek zamanlı olarak tespit eden ve metne dönüştüren web tabanlı 
bir sistemdir[cite: 1]. YOLO11 nesne tespiti ve EasyOCR motorunun gücünü birleştiren 
bu proje, zorlu çevre koşullarına karşı gelişmiş OpenCV görüntü ön işleme 
(CLAHE, Otsu, Morfoloji) teknikleriyle OCR başarısını maksimize eder[cite: 1].

[ TEMEL ÖZELLİKLER ]
* Gerçek Zamanlı Tespit: Flask-SocketIO (Eventlet) ile kamera akışından gelen 
  kareler asenkron olarak arka plana iletilir ve anlık olarak işlenir[cite: 1].
* Yüksek Hassasiyet (YOLO11): Sadece %70 güven (confidence) eşiğini geçen 
  plaka tespitleri işleme alınır. OCR'ın metni daha rahat okuması için plaka 
  bölgesi (ROI) kenarlardan 5'er piksel genişletilir[cite: 1].
* Gelişmiş Görüntü Ön İşleme: Kırpılan plaka bölgesi gri tonlamaya çevrilir, 
  çözünürlüğü 2 kat (CUBIC) büyütülür, CLAHE ile kontrast dengelenir ve 
  Morfolojik (Açma/Kapama) işlemlerle yazılar pürüzsüzleştirilir[cite: 1].
* Akıllı Karakter Düzeltme (Regex): OCR'ın sık yaptığı O ve 0 karışıklığı 
  Türkiye plaka formatına (İl kodu + Harf + Rakam) göre otomatik onarılır[cite: 1].
  İl kodunun 01-81 aralığında olup olmadığı doğrulanır[cite: 1].
* Otomatik Arşivleme: Doğrulanan plakalar, zaman damgası ve plaka adıyla 
  birlikte yerel diskinizdeki 'Tespitler' klasörüne (.jpg) kaydedilir[cite: 1].

[ GİRDİ VE ÇIKTI (Örnek API Yanıtı) ]
Sistem kameradan yakalanan hedef kareyi Base64 formatında (/detect) alır ve 
yapılandırılmış bir JSON objesi döndürür[cite: 1]:

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

[ PROJE YAPISI ]
- app.py                : Web sunucusunu (Flask), YOLO11 ve EasyOCR modellerini
                          çalıştıran, görüntü işleme ve Regex mantığını 
                          barındıran ana dosyadır[cite: 1].
- templates/index.html  : Kamerayı açan, video karelerini arka plana ileten 
                          ve plaka geçmişini (history) listeleyen arayüz[cite: 1].
- best.pt               : Özel olarak eğitilmiş YOLO11 plaka tespit ağırlığı[cite: 1].
- Tespitler/            : Başarıyla okunan plakaların arşivlendiği klasör[cite: 1].

[ KURULUM VE ÇALIŞTIRMA ]
(Not: Hızlı OCR okuması için NVIDIA GPU (CUDA) tavsiye edilir[cite: 1].)

1. Depoyu indirin ve klasöre girin:
   git clone https://github.com/hserhatizmirli/Plate-Detect-System.git
   cd Plate-Detect-System

2. Bağımlılıkları (requirements) yükleyin:
   pip install flask flask-socketio flask-cors easyocr ultralytics opencv-python numpy polars

3. Dosya yollarını ayarlayın ve uygulamayı başlatın:
   (app.py içindeki MODEL_PATH ve SAVE_DIR yollarını bilgisayarınıza göre 
   düzenledikten sonra aşağıdaki komutu çalıştırın)[cite: 1]
   python app.py

4. Tarayıcınızdan sisteme erişin:
   http://localhost:5000 veya yerel ağ IP'niz üzerinden giriş yapın.
   (Kamera erişim izni istendiğinde onay verin.)

================================================================================
