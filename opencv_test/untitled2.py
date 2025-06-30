import cv2
import numpy as np

# استفاده از الگوریتم پیشرفته KNN برای background subtraction
back_sub = cv2.createBackgroundSubtractorKNN(history=500, dist2Threshold=400, detectShadows=True)

# تابع برای محاسبه مرکز (centroid)
def get_centroid(x, y, w, h):
    return (int(x + w / 2), int(y + h / 2))

# ایجاد یک فیلتر کالمن برای پیگیری حرکت شیء
kalman = cv2.KalmanFilter(4, 2)
kalman.transitionMatrix = np.array([[1, 0, 1, 0],
                                    [0, 1, 0, 1],
                                    [0, 0, 1, 0],
                                    [0, 0, 0, 1]], np.float32)
kalman.measurementMatrix = np.array([[1, 0, 0, 0],
                                     [0, 1, 0, 0]], np.float32)
kalman.processNoiseCov = np.array([[1e-2, 0, 0, 0],
                                   [0, 1e-2, 0, 0],
                                   [0, 0, 1, 0],
                                   [0, 0, 0, 1]], np.float32)
kalman.errorCovPost = np.eye(4, dtype=np.float32)
kalman.statePost = np.zeros((4, 1), np.float32)

# گرفتن تصویر از دوربین
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # تبدیل تصویر به خاکستری
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # دریافت ماسک اشیاء متحرک
    fg_mask = back_sub.apply(frame)

    # اعمال عملیات مورفولوژیکی برای حذف سایه‌ها و نویز
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5))
    fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel, iterations=1)
    fg_mask = cv2.dilate(fg_mask, kernel, iterations=1)

    # پیدا کردن کانتورها
    contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 100:  # فقط اشیاء بزرگتر از این اندازه رو بررسی کن
            x, y, w, h = cv2.boundingRect(cnt)
            centroid = get_centroid(x, y, w, h)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.circle(frame, centroid, 4, (0, 0, 255), -1)
            cv2.putText(frame, "Moving Object", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            # اندازه‌گیری موقعیت شیء و پیش‌بینی با فیلتر کالمن
            kalman.correct(np.array([x + w / 2, y + h / 2], np.float32))
            prediction = kalman.predict()
            
            # استخراج مقادیر پیش‌بینی شده
            predicted_x, predicted_y = int(prediction[0, 0]), int(prediction[1, 0])
            
            # رسم موقعیت پیش‌بینی شده
            cv2.circle(frame, (predicted_x, predicted_y), 4, (255, 0, 0), -1)

    # نمایش تصویر پردازش شده
    cv2.imshow('Real-Time Object Tracking with Kalman Filter', frame)

    # خروج از برنامه با کلید ESC
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
