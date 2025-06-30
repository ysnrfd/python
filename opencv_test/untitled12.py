import cv2
import numpy as np
import time
from sklearn.neighbors import KNeighborsClassifier
from collections import defaultdict, deque

# Create background subtractor for motion detection
back_sub = cv2.createBackgroundSubtractorKNN(history=500, dist2Threshold=400, detectShadows=True)
cap = cv2.VideoCapture(0)

# Store object traces
object_traces = defaultdict(lambda: deque(maxlen=30))  # Last 30 points of each object
object_last_seen = {}
object_id_counter = 0

# For real-time learning
knn = KNeighborsClassifier(n_neighbors=3)
features_set = []
labels_set = []

# Timer for real-time learning and training interval
start_time = time.time()
training_interval = 5  # 5 seconds for real-time training

# Variable to avoid predicting before training
is_trained = False

# Memory storage for past predictions and features
memory = defaultdict(list)  # Store memory of features and predictions for each object

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
        return "Left" if dx < 0 else "Right"
    else:
        return "Up" if dy < 0 else "Down"

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
        if dx1 * dx2 < 0:  # Horizontal direction change
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
    predicted = 1  # Default prediction value (if no prediction is made)
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < 150:
            continue

        x, y, w, h = cv2.boundingRect(cnt)
        centroid = get_centroid(x, y, w, h)

        # Identify or create a new ID for the object
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

        # Feature for the model
        feature = [w, h, centroid[0], centroid[1], area, speed, direction_changes]
        label = 1  # Default label: Normal

        # Simple automatic labeling:
        if speed > 100 or direction_changes > 4:
            label = 2  # Suspicious

        features_set.append(feature)
        labels_set.append(label)

        # Store features and predictions in memory
        memory[matched_id].append({
            'features': feature,
            'prediction': label
        })

        # Retrain the model every 5 seconds
        if time.time() - start_time > training_interval:
            if len(features_set) > 10:
                knn.fit(features_set, labels_set)  # Train the model
                is_trained = True  # Model is trained
                print("Model updated.")
                start_time = time.time()  # Reset the timer after retraining

        # Prediction only after training
        if is_trained:
            predicted = knn.predict([feature])[0]

        # Draw information on the frame
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0) if label == 1 else (0, 0, 255), 2)
        cv2.circle(frame, centroid, 4, (255, 255, 255), -1)
        cv2.putText(frame, f"ID: {matched_id} | Direction: {direction} | Speed: {int(speed)}", (x, y - 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
        cv2.putText(frame, f"Behavior: {'Normal' if predicted == 1 else 'Suspicious'}", (x, y - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

    # Remove old object IDs from memory
    for oid in list(object_last_seen):
        if time.time() - object_last_seen[oid] > 2:
            object_traces.pop(oid, None)
            object_last_seen.pop(oid, None)
            memory.pop(oid, None)  # Remove from memory as well

    cv2.imshow("Behavioral Intelligence", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
