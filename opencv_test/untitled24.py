import cv2
from ultralytics import YOLO

# بارگذاری مدل YOLOv8 از پیش آموزش‌دیده
model = YOLO("yolo12l.pt")  # مدل‌های مختلف: yolov8n.pt, yolov8s.pt, yolov8m.pt

# استفاده از دوربین برای تشخیص اشیا به صورت real-time
cap = cv2.VideoCapture(0)  # 0 برای استفاده از دوربین پیش‌فرض سیستم

while True:
    ret, frame = cap.read()
    
    if not ret:
        break
    
    # انجام تشخیص روی هر فریم از ویدیو
    results = model(frame)
    
    # نتایج مدل در قالب لیستی از اشیا است
    result = results[0]  # گرفتن اولین نتیجه
    
    # نمایش فریم با نتایج پیش‌بینی شده
    frame_with_boxes = result.plot()  # تصویر با جعبه‌های شناسایی شده
    cv2.imshow('Real-Time Object Detection', frame_with_boxes)  # نمایش فریم با جعبه‌ها
    
    # بررسی اگر کلید "q" فشار داده شد برای بستن ویدیو
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# آزادسازی منابع
cap.release()
cv2.destroyAllWindows()
