import cv2
import numpy as np
from sklearn.neighbors import KNeighborsClassifier

# استفاده از الگوریتم پیشرفته KNN برای background subtraction
back_sub = cv2.createBackgroundSubtractorKNN(history=500, dist2Threshold=400, detectShadows=True)

# تابع برای محاسبه مرکز (centroid)
def get_centroid(x, y, w, h):
    return (int(x + w / 2), int(y + h / 2))

# تابع برای کاهش نویز
def apply_noise_reduction(fg_mask):
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel, iterations=2)
    fg_mask = cv2.dilate(fg_mask, kernel, iterations=1)
    return fg_mask

# تابع برای تشخیص جهت حرکت
def detect_direction(prev, curr):
    dx = curr[0] - prev[0]
    dy = curr[1] - prev[1]
    if abs(dx) > abs(dy):
        return "Right" if dx > 0 else "Left"
    else:
        return "Down" if dy > 0 else "Up"

# گرفتن تصویر از دوربین
cap = cv2.VideoCapture(0)

# مدل KNN
knn = KNeighborsClassifier(n_neighbors=3)

# داده‌های آموزشی و برچسب‌ها
object_features = []
object_labels = []

# تنظیمات آموزش دوره‌ای
learning_interval = 30
frame_count = 0

# نگه‌داری آخرین موقعیت centroid برای دنبال‌ کردن مسیر
prev_centroids = []

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    fg_mask = back_sub.apply(frame)
    fg_mask = apply_noise_reduction(fg_mask)
    contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    current_centroids = []

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 100:
            x, y, w, h = cv2.boundingRect(cnt)
            centroid = get_centroid(x, y, w, h)
            current_centroids.append(centroid)

            # استخراج ویژگی‌ها
            features = [w, h, centroid[0], centroid[1], area]
            object_features.append(features)
            object_labels.append(1)

            # رسم باکس و مرکز
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.circle(frame, centroid, 4, (0, 0, 255), -1)

            # اگر centroid قبلی موجود است، جهت را تشخیص بده
            if len(prev_centroids) > 0:
                closest_prev = min(prev_centroids, key=lambda p: np.linalg.norm(np.array(p) - np.array(centroid)))
                direction = detect_direction(closest_prev, centroid)
                cv2.putText(frame, f"Dir: {direction}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

    # به‌روزرسانی centroid های قبلی
    prev_centroids = current_centroids.copy()

    # آموزش دوره‌ای مدل
    frame_count += 1
    if frame_count % learning_interval == 0 and len(object_features) > 5:
        knn.fit(object_features, object_labels)
        print("Model updated!")

    if len(object_features) > 5 and frame_count % learning_interval == 0:
        predicted_label = knn.predict([features])[0]
        cv2.putText(frame, f"Predicted: {predicted_label}", (x, y - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    # نمایش تصویر
    cv2.imshow('Object Tracking with Direction', frame)

    # خروج با کلید ESC
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
