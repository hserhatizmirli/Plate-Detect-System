import cv2
import os
import re
import base64
import numpy as np
from datetime import datetime
import easyocr
from ultralytics import YOLO
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# === KONFİGÜRASYON ===
MODEL_PATH = r'C:\Users\HSİ\Desktop\Plaka Tanıma Sistemi\Yolo\runs\detect\yolo11\weights\best.pt'
SAVE_DIR = r'C:\Users\HSİ\Desktop\Plaka Tanıma Sistemi\Tespitler'
os.makedirs(SAVE_DIR, exist_ok=True)

print("="*50)
print("PLAKA TANIMA SİSTEMİ BAŞLATILIYOR...")
print("="*50)

# === MODELLERİ YÜKLE ===
print("YOLO modeli yükleniyor...")
model = YOLO(MODEL_PATH)
print(f"YOLO yüklendi: {model.names}")

print("OCR modeli yükleniyor (bu biraz zaman alabilir)...")
reader = easyocr.Reader(['tr', 'en'], gpu=True)
print("OCR hazır.")

# === GEÇMİŞ ===
history = []
last_saved_plate = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/detect', methods=['POST'])
def detect_plate():
    global last_saved_plate, history
    
    try:
        data = request.json
        if not data or 'image' not in data:
            return jsonify({'error': 'Görüntü verisi eksik'}), 400
            
        image_data = data['image'].split(',')[1]
        image_bytes = base64.b64decode(image_data)
        np_array = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
        
        if frame is None:
            return jsonify({'error': 'Geçersiz görüntü'}), 400
        
        results = model(frame, conf=0.70, iou=0.3, verbose=False)
        annotated = results[0].plot()
        
        plate_info = None
        
        if results[0].boxes is not None:
            for box in results[0].boxes:
                conf = float(box.conf[0])
                if conf > 0.60:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    h, w = frame.shape[:2]
                    x1, y1 = max(0, x1-5), max(0, y1-5)
                    x2, y2 = min(w, x2+5), min(h, y2+5)
                    roi = frame[y1:y2, x1:x2]
                    
                    if roi.size > 0:
                        ocr_result = reader.readtext(roi)
                        raw_text = ""
                        total_conf = 0
                        count = 0
                        
                        for (bbox, text, prob) in ocr_result:
                            if prob > 0.65:
                                raw_text += text.upper()
                                total_conf += prob
                                count += 1
                        
                        cleaned = re.sub(r'[^A-Z0-9]', '', raw_text)
                        if cleaned.startswith("TR"):
                            cleaned = cleaned[2:]
                        
                        match = re.search(r"(0[1-9]|[1-7][0-9]|8[01])([A-Z]{1,3})(\d{2,4})", cleaned)
                        
                        if match and count > 0:
                            plate = f"{match.group(1)} {match.group(2)} {match.group(3)}"
                            ocr_conf = (total_conf / count) * 100
                            
                            plate_info = {
                                'plate': plate,
                                'yolo_conf': round(conf * 100, 2),
                                'ocr_conf': round(ocr_conf, 2),
                                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            }
                            
                            if plate != last_saved_plate:
                                filename = f"{plate.replace(' ', '_')}_{int(datetime.now().timestamp())}.jpg"
                                save_path = os.path.join(SAVE_DIR, filename)
                                cv2.imwrite(save_path, roi)
                                last_saved_plate = plate
                                history.append({
                                    'plate': plate,
                                    'time': plate_info['timestamp'],
                                    'image': filename
                                })
                                print(f"Yeni plaka kaydedildi: {plate}")
                            
                            _, buffer = cv2.imencode('.jpg', annotated)
                            annotated_b64 = base64.b64encode(buffer).decode('utf-8')
                            
                            return jsonify({
                                'success': True,
                                'plate_info': plate_info,
                                'annotated_image': annotated_b64
                            })
        
        return jsonify({'success': False, 'message': 'Plaka tespit edilemedi'})
        
    except Exception as e:
        print(f"Hata: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/history')
def get_history():
    return jsonify(history)

@app.route('/clear_history', methods=['POST'])
def clear_history():
    global history, last_saved_plate
    history = []
    last_saved_plate = None
    print("Geçmiş temizlendi")
    return jsonify({'success': True})

if __name__ == '__main__':

    print("="*50)
    print("SUNUCU BAŞLATILIYOR (TAMAMEN YEREL HTTPS MODU)...")
    print("Güvenlik aktif: İnternete kapalıdır, sadece şirket ağına bağlı cihazlar girebilir.")
    print("="*50)
    
    # Yerel ağda kameraya erişebilmek için adhoc ile sahte ssl oluşturuyoruz
    app.run(host='127.0.0.1', port=5000, debug=False, threaded=True)


# if __name__ == '__main__':
#     print("="*50)
#     print("SUNUCU BAŞLATILIYOR (TÜNEL İÇİN HTTP MODU)...")
#     print("DİKKAT: Ngrok veya Localtunnel'ı ayrı bir terminalden başlatmayı unutmayın!")
#     print("="*50)
#     app.run(host='0.0.0.0', port=5000, debug=False)