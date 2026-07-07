import cv2
import os
import re
import easyocr
from ultralytics import YOLO
from multiprocessing import freeze_support

# Model eğitim parametreleri // Model training parameters
# Kendi yolunuza göre değiştirin // Change your path according to your own
def model_train(egitilecek_model):
    egitilecek_model.train(
        cache=False,
        amp=False,
        imgsz=[640, 480],
        batch=8,
        workers=4,
        device=0,
        data="C:/Users/HSİ/Desktop/Plaka Tanıma Sistemi/Dataset/data.yaml", 
        epochs=150,
        patience=50,
        name='yolo11',
        project='C:/Users/HSİ/Desktop/Plaka Tanıma Sistemi/Yolo/runs/detect',
        exist_ok=True,
        
        
    )

def kamera():
    # Modelin yolu (Kendi yolunuza göre değiştirin) // Path to the model (Change your model path according to your own)
    best_pt = r'C:\Users\HSİ\Desktop\Plaka Tanıma Sistemi\Yolo\runs\detect\yolo11\weights\best.pt'
    
    if not os.path.exists(best_pt):
        print(f"Eğitilmiş model bulunamadı! Aranan yol: {best_pt}")
        return
        
    model = YOLO(best_pt)
    print(f"YOLO Modeli yüklendi: {model.names}")
    
    print("OCR (Metin Okuma) Modeli yükleniyor... Lütfen bekleyin...")
    reader = easyocr.Reader(['tr', 'en'], gpu=True) # Ana önceliği Türkçe ve sonrasında İngilizce olarak ayarladık. // We set the main priority to Turkish and then English.
    print("Sistem hazır!")

    # EKRAN GÖRÜNTÜLERİNİN KAYDEDİLECEĞİ KLASÖR // Folder where the screenshots will be saved
    kayit_klasoru = r'C:\Users\HSİ\Desktop\Plaka Tanıma Sistemi\Tespitler'
    os.makedirs(kayit_klasoru, exist_ok=True)
    # opencv ile kamerayı açıyoruz ve 0 ile ana bilgisayar kamerasını seçiyoruz. // We open the camera with opencv and select the main computer camera with 0.
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    if not cap.isOpened():
        print("Kamera açılamadı!")
        return

    print("Kamera çalışıyor. Çıkmak için 'q' tuşuna basın.")
    # Kameradan frame alıyorsa devam et // if ı get the frame from the camera, continue
    while True:
        ret, frame = cap.read()
        if not ret:
            continue
        # Güven eşiği ve labelların üst üste binme oranını ayarlıyoruz. // We set the confidence threshold and the overlap ratio of the labels.    
        results = model(frame, conf=0.70, iou=0.3, verbose=False)
        annotated_frame = results[0].plot() # Gelen sonuçlar verdiğimiz değerlere uygunsa kamera üzerinde kutu çiziyoruz 
                                            # if ı get the results, we draw aa box on the camera if they are appropriate for the values we give
        # Tespit edilen görsel kontorlünü yapıyoruz. // We check the detected image.
        if results[0].boxes is not None:
            for box in results[0].boxes:
                conf = float(box.conf[0])
                # YOLO güven oranı %70'in üzerindeyse
                if conf > 0.70:
                    # Tespit edilen plakanın koordinatlarını alıyoruz. // We get the coordinates of the detected plate.
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    # Görüntü boyutlarını alıp 5px büyütüyoruz. // We get the image dimensions and enlarge it by 5px.
                    h, w = frame.shape[:2]
                    x1, y1 = max(0, x1-5), max(0, y1-5)
                    x2, y2 = min(w, x2+5), min(h, y2+5)
                    # Seçtiğimiz alanın fotoğrafını alıyoruz. // We take a photo of the area we selected.
                    foto = frame[y1:y2, x1:x2]
                    # Seçili fotoğrafı kaydedip görüntü işleme fonksiyonlarıyla OCR'a gönderiyoruz. // We save the selected photo and send it to OCR with image processing functions.
                    if foto.size > 0:
                        dosya_yolu = os.path.join(kayit_klasoru, "son_tespit.jpg")
                        cv2.imwrite(dosya_yolu, foto)
                        cv2.imshow('Kaydedilen SS (Plaka)', foto)
                        ocr_sonuclari = reader.readtext(foto)
                        
                        # OCR' dan gelen verileri tek metin olarak birleştiriyoruz ve güven oranlarını hesaplıyoruz. // We combine the data from OCR into a single text and calculate the confidence rates.
                        raw_text = ""
                        ortalama_guven = 0
                        parca_sayisi = 0
                        # Metindeki her bir parçayı büyük harfe çevirip güven oranını hesaplıyoruz. // We convert each piece of text to uppercase and calculate the confidence rate.
                        for (bbox, text, prob) in ocr_sonuclari:
                            # OCR güven oranı %65'in üzerindeyse her bir parçanın güven oranı yüksek olanları birleştiriyoruz. // If the OCR confidence rate is above 65%, we combine the ones with high confidence rate.
                            if prob > 0.65:
                                raw_text += text.upper()
                                ortalama_guven += prob
                                parca_sayisi += 1
                                
                        
                        # 1. Sadece İngilizce A-Z harflerini ve 0-9 rakamlarını bırak. 
                        # Tüm boşlukları, ], }, !, % gibi işaretleri yok et.
                        cleaned_text = re.sub(r'[^A-Z0-9]', '', raw_text)
                        
                        # 2. Eğer OCR mavi şeritteki TR'yi okuyup en başa koyduysa onu sil
                        if cleaned_text.startswith("TR"):
                            cleaned_text = cleaned_text[2:]
                            
                        # 3. REGEX ile Türkiye Plaka Formatını Ara:
                        # Kural: (01 ile 81 arası sayı) + (1 ile 3 arası harf) + (2 ile 4 arası sayı)
                        match = re.search(r"(0[1-9]|[1-7][0-9]|8[01])([A-Z]{1,4})([0-9]{2,4})", cleaned_text)
                        
                        # Eğer okunan metin Türkiye plaka kurallarına uyuyorsa ekrana yazdır
                        if match and parca_sayisi > 0:
                            il_kodu = match.group(1)
                            harfler = match.group(2)
                            rakamlar = match.group(3)
                            
                            # Parçaları nizami bir şekilde boşluklu birleştir
                            tam_plaka = f"{il_kodu} {harfler} {rakamlar}"
                            g_orani = (ortalama_guven / parca_sayisi) * 100
                            
                            print(f"{'='*40}")
                            print(f" SS Kaydedildi: {dosya_yolu}")
                            print(f"YOLO Güveni : %{conf*100:.1f}")
                            print(f"TAM PLAKA   : {tam_plaka}")
                            print(f"OCR Güveni  : %{g_orani:.1f}")
                            print(f"{'='*40}\n")
        # Kullanıcıya gösterdiğmiz kamera ekranı // The camera screen we show to the user
        cv2.imshow('Plaka Tespiti (Ana Kamera)', annotated_frame)
        # Klavye girişini kontrol eder ve 'q' tuşuna basıldığında döngüyü kırar. 
        # # Checks the keyboard input and breaks the loop when the 'q' key is pressed.
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    # Kamera ve opencv pencerelerini kapatır. // Closes the camera and opencv windows.
    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    freeze_support()
    
    # 1. Önce modeli indir / yükle
    baslangic_modeli = YOLO('yolo11n.pt')
    
    # 2. Modeli eğitim fonksiyonuna gönder
    #model_train(baslangic_modeli)
    kamera()