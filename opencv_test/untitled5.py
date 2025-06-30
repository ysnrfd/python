import cv2
import numpy as np
from sklearn.neighbors import KNeighborsClassifier

# استفاده از الگوریتم پیشرفته KNN برای background subtraction
back_sub = cv2.createBackgroundSubtractorKNN(history=500, dist2Threshold=400, detectShadows=True)

# تابع برای محاسبه مرکز (centroid)
def get_centroid(x, y, w, h):
    return (int(x + w / 2), int(y + h / 2))

# گرفتن تصویر از دوربین
cap = cv2.VideoCapture(0)

# مدل KNN
knn = KNeighborsClassifier(n_neighbors=3)

# داده‌های آموزشی و برچسب‌ها
object_features = []
object_labels = []

# تنظیمات برای آموزش دوره‌ای
learning_interval = 30  # هر 30 فریم یک بار آموزش انجام شود
frame_count = 0

# استفاده از فیلتر برای کاهش نویز
def apply_noise_reduction(fg_mask):
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel, iterations=2)  # حذف نویز به‌وسیله باز کردن
    fg_mask = cv2.dilate(fg_mask, kernel, iterations=1)  # گسترش اشیاء برای تقویت
    return fg_mask

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # تبدیل تصویر به خاکستری
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # دریافت ماسک اشیاء متحرک
    fg_mask = back_sub.apply(frame)

    # اعمال فیلتر برای کاهش نویز
    fg_mask = apply_noise_reduction(fg_mask)

    # پیدا کردن کانتورها
    contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 100:  # فقط اشیاء بزرگتر از این اندازه رو بررسی کن
            x, y, w, h = cv2.boundingRect(cnt)
            centroid = get_centroid(x, y, w, h)
            
            # استخراج ویژگی‌ها
            features = [w, h, centroid[0], centroid[1], area]  # اضافه کردن مساحت به ویژگی‌ها
            object_features.append(features)
            object_labels.append(1)  # فرض می‌کنیم همه اشیاء متحرک به کلاس 1 تعلق دارند

            # رسم باکس و مرکز
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.circle(frame, centroid, 4, (0, 0, 255), -1)

    # آموزش مدل به صورت دوره‌ای
    frame_count += 1
    if frame_count % learning_interval == 0 and len(object_features) > 5:
        # آموزش مدل فقط زمانی که داده‌ها کافی باشند
        knn.fit(object_features, object_labels)
        print("Model updated!")

    # پیش‌بینی با مدل KNN برای اشیاء جدید
    if len(object_features) > 5 and frame_count % learning_interval == 0:
        # اطمینان حاصل می‌کنیم که مدل آموزش داده شده است قبل از پیش‌بینی
        predicted_label = knn.predict([features])[0]
        cv2.putText(frame, f"Predicted: {predicted_label}", (x, y - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    # نمایش تصویر
    cv2.imshow('Optimized Object Tracking', frame)

    # خروج از برنامه با کلید ESC
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
