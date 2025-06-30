import cv2
import numpy as np
import time
from sklearn.neighbors import KNeighborsClassifier
from collections import defaultdict, deque

back_sub = cv2.createBackgroundSubtractorKNN(history=500, dist2Threshold=400, detectShadows=True)
cap = cv2.VideoCapture(0)

# ذخیره مسیر اشیاء
object_traces = defaultdict(lambda: deque(maxlen=30))  # آخرین ۳۰ نقطه هر شیء
object_last_seen = {}
object_id_counter = 0

# برای یادگیری real-time
knn = KNeighborsClassifier(n_neighbors=3)
features_set = []
labels_set = []
frame_count = 0
learning_interval = 30

def apply_noise_reduction(mask):
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=2)
    mask = cv2.dilate(mask, kernel, iterations=1)
    return mask

def get_centroid(x, y, w, h):
    return (int(x + w / 2), int(y + h / 2))

def calculate_direction(trace):
    if len(trace) < 2:
        return "-"
    dx = trace[-1][0] - trace[0][0]
    dy = trace[-1][1] - trace[0][1]
    if abs(dx) > abs(dy):
        return "چپ" if dx < 0 else "راست"
    else:
        return "بالا" if dy < 0 else "پایین"

def calculate_speed(trace, duration):
    if len(trace) < 2 or duration == 0:
        return 0
    dist = np.linalg.norm(np.array(trace[-1]) - np.array(trace[0]))
    return dist / duration

def count_direction_changes(trace):
    changes = 0
    for i in range(2, len(trace)):
        dx1 = trace[i-1][0] - trace[i-2][0]
        dx2 = trace[i][0] - trace[i-1][0]
        if dx1 * dx2 < 0:  # تغییر جهت افقی
            changes += 1
    return changes

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    fg_mask = back_sub.apply(frame)
    fg_mask = apply_noise_reduction(fg_mask)

    contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    current_ids = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < 150:
            continue

        x, y, w, h = cv2.boundingRect(cnt)
        centroid = get_centroid(x, y, w, h)

        # شناسایی یا ایجاد شناسه جدید
        matched_id = None
        for oid, trace in object_traces.items():
            if np.linalg.norm(np.array(trace[-1]) - np.array(centroid)) < 50:
                matched_id = oid
                break

        if matched_id is None:
            matched_id = object_id_counter
            object_id_counter += 1

        object_traces[matched_id].append(centroid)
        object_last_seen[matched_id] = time.time()
        current_ids.append(matched_id)

        trace = object_traces[matched_id]
        duration = time.time() - object_last_seen[matched_id] + 0.001
        speed = calculate_speed(trace, duration)
        direction = calculate_direction(trace)
        direction_changes = count_direction_changes(trace)
        total_move = sum(np.linalg.norm(np.array(trace[i]) - np.array(trace[i-1])) for i in range(1, len(trace)))

        # ویژگی برای مدل
        feature = [w, h, centroid[0], centroid[1], area, speed, direction_changes]
        label = 1  # کلاس پیش‌فرض: عادی

        # برچسب‌گذاری خودکار ساده:
        if speed > 100 or direction_changes > 4:
            label = 2  # مشکوک

        features_set.append(feature)
        labels_set.append(label)

        if len(features_set) > 10 and frame_count % learning_interval == 0:
            knn.fit(features_set, labels_set)
            print("مدل به‌روزرسانی شد.")

        predicted = "-"
        if len(features_set) > 10:
            predicted = knn.predict([feature])[0]

        # رسم اطلاعات روی فریم
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0) if label == 1 else (0, 0, 255), 2)
        cv2.circle(frame, centroid, 4, (255, 255, 255), -1)
        cv2.putText(frame, f"ID: {matched_id} | جهت: {direction} | سرعت: {int(speed)}", (x, y - 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
        cv2.putText(frame, f"رفتار: {'عادی' if predicted == 1 else 'مشکوک'}", (x, y - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

    frame_count += 1

    # حذف آی‌دی‌های قدیمی
    for oid in list(object_last_seen):
        if time.time() - object_last_seen[oid] > 2:
            object_traces.pop(oid, None)
            object_last_seen.pop(oid, None)

    cv2.imshow("هوش رفتاری", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
