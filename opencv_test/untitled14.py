import cv2
import numpy as np
from collections import deque, defaultdict
import time

# پارامترها
trace_len = 20
min_area = 500

# حافظه
object_traces = defaultdict(lambda: deque(maxlen=trace_len))
long_term_memory = defaultdict(list)
next_object_id = 1
object_centroids = {}

def count_direction_changes(trace):
    count = 0
    for i in range(2, len(trace)):
        v1 = np.array(trace[i - 1]) - np.array(trace[i - 2])
        v2 = np.array(trace[i]) - np.array(trace[i - 1])
        if np.dot(v1, v2) < 0:
            count += 1
    return count

def extract_features(trace):
    if len(trace) < 2:
        return [0, 0, 0, 0]
    dx = trace[-1][0] - trace[0][0]
    dy = trace[-1][1] - trace[0][1]
    total_distance = sum(np.linalg.norm(np.array(trace[i]) - np.array(trace[i-1])) for i in range(1, len(trace)))
    avg_speed = total_distance / (len(trace) + 1e-6)
    direction_changes = count_direction_changes(trace)
    return [dx, dy, avg_speed, direction_changes]

def ai_brain(trace, memory):
    if len(trace) < 3:
        return "Unknown"
    dx, dy, speed, changes = extract_features(trace)

    if len(memory) >= 5 and memory.count("Erratic") > 3:
        return "Suspicious"
    if speed > 150 and changes > 4:
        return "Erratic"
    if speed < 5 and changes == 0:
        return "Idle"
    return "Normal"

def get_color(i):
    np.random.seed(i)
    return tuple(int(x) for x in np.random.randint(100, 255, 3))

# آماده‌سازی دوربین
cap = cv2.VideoCapture(0)
ret, prev = cap.read()
prev_gray = cv2.cvtColor(prev, cv2.COLOR_BGR2GRAY)
prev_gray = cv2.GaussianBlur(prev_gray, (21, 21), 0)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray_blur = cv2.GaussianBlur(gray, (21, 21), 0)

    # محاسبه اختلاف فریم‌ها
    delta = cv2.absdiff(prev_gray, gray_blur)
    thresh = cv2.threshold(delta, 25, 255, cv2.THRESH_BINARY)[1]
    thresh = cv2.dilate(thresh, None, iterations=2)

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    current_centroids = []

    for cnt in contours:
        if cv2.contourArea(cnt) < min_area:
            continue
        (x, y, w, h) = cv2.boundingRect(cnt)
        cx, cy = x + w // 2, y + h // 2
        current_centroids.append((cx, cy))
        matched_id = None

        # تطبیق با شیء قبلی
        for object_id, last_centroid in object_centroids.items():
            if np.linalg.norm(np.array([cx, cy]) - np.array(last_centroid)) < 50:
                matched_id = object_id
                break

        if matched_id is None:
            matched_id = next_object_id
            next_object_id += 1

        object_centroids[matched_id] = (cx, cy)
        object_traces[matched_id].append((cx, cy))
        trace = object_traces[matched_id]

        behavior = ai_brain(trace, [m['status'] for m in long_term_memory[matched_id]])
        long_term_memory[matched_id].append({'status': behavior, 'timestamp': time.time()})

        color = get_color(matched_id)
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
        cv2.putText(frame, f"ID {matched_id}", (x, y - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        cv2.putText(frame, f"Behavior: {behavior}", (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

    # پاکسازی اشیاء غیرفعال
    inactive_ids = [obj_id for obj_id in object_centroids if obj_id not in [id for id, _ in object_centroids.items()]]
    for iid in inactive_ids:
        object_centroids.pop(iid, None)

    prev_gray = gray_blur.copy()
    cv2.imshow("Motion AI", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
