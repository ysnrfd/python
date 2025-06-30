import cv2
import numpy as np

# استفاده از الگوریتم پیشرفته KNN برای background subtraction
back_sub = cv2.createBackgroundSubtractorKNN(history=500, dist2Threshold=400, detectShadows=True)

# تابع برای محاسبه مرکز (centroid)
def get_centroid(x, y, w, h):
    return (int(x + w / 2), int(y + h / 2))

# گرفتن تصویر از دوربین
cap = cv2.VideoCapture(0)

# Kalman Filter برای ردیابی دقیق‌تر
kalman = cv2.KalmanFilter(4, 2)
kalman.measurementMatrix = np.array([[1, 0, 0, 0], [0, 1, 0, 0]], np.float32)
kalman.transitionMatrix = np.array([[1, 0, 1, 0], [0, 1, 0, 1], [0, 0, 1, 0], [0, 0, 0, 1]], np.float32)
kalman.processNoiseCov = np.array([[1e-5, 0, 0, 0], [0, 1e-5, 0, 0], [0, 0, 1e-5, 0], [0, 0, 0, 1e-5]], np.float32)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # تبدیل تصویر به خاکستری
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # دریافت ماسک اشیاء متحرک
    fg_mask = back_sub.apply(frame)

    # حذف نویز پیشرفته با استفاده از GaussianBlur و MedianBlur
    fg_mask = cv2.GaussianBlur(fg_mask, (5, 5), 0)  # حذف نویز با بلور گوسی
    fg_mask = cv2.medianBlur(fg_mask, 5)  # حذف نویز با استفاده از MedianBlur

    # اعمال عملیات مورفولوژیکی پیچیده‌تر برای حذف نویز و سایه‌ها
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))  # هسته بزرگتر
    fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel, iterations=2)  # استفاده از عملیات CLOSE
    fg_mask = cv2.dilate(fg_mask, kernel, iterations=3)  # افزایش سایز ماسک

    # پیدا کردن کانتورها
    contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 500:  # فقط اشیاء بزرگتر از این اندازه رو بررسی کن
            x, y, w, h = cv2.boundingRect(cnt)
            centroid = get_centroid(x, y, w, h)
            
            # استفاده از Kalman Filter برای پیش‌بینی موقعیت شیء
            kalman.correct(np.array([np.float32(centroid[0]), np.float32(centroid[1])]))
            prediction = kalman.predict()
            
            predicted_x, predicted_y = int(prediction[0]), int(prediction[1])
            
            # رسم باکس و پیش‌بینی موقعیت
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.circle(frame, centroid, 4, (0, 0, 255), -1)
            cv2.putText(frame, "Moving Object", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.circle(frame, (predicted_x, predicted_y), 4, (255, 0, 0), -1)  # پیش‌بینی موقعیت

    # نمایش تصویر
    cv2.imshow('Optimized Object Tracking', frame)

    # خروج از برنامه با کلید ESC
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
