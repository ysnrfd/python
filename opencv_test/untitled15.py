import cv2
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np

# ======== AI MODEL (PyTorch) ========
device = torch.device("cpu")

label_map = {"Idle": 0, "Normal": 1, "Erratic": 2}
reverse_label = {v: k for k, v in label_map.items()}

class BehaviorAI(nn.Module):
    def __init__(self):
        super().__init__()
        self.model = nn.Sequential(
            nn.Linear(4, 16),
            nn.ReLU(),
            nn.Linear(16, 8),
            nn.ReLU(),
            nn.Linear(8, 3)
        )
        self.loss_fn = nn.CrossEntropyLoss()
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.001)
    
    def forward(self, x):
        return self.model(x)

    def predict_behavior(self, features):
        self.model.eval()
        with torch.no_grad():
            x = torch.tensor([features], dtype=torch.float32).to(device)
            logits = self.model(x)
            pred = torch.argmax(logits, dim=-1).item()
            return reverse_label[pred]

    def learn_from(self, features, label):
        self.model.train()
        x = torch.tensor([features], dtype=torch.float32).to(device)
        y = torch.tensor([label_map[label]], dtype=torch.long).to(device)
        logits = self.model(x)
        loss = self.loss_fn(logits, y)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

# ======== FEATURE EXTRACTION ========
def extract_features(trace):
    if len(trace) < 2:
        return [0, 0, 0, 0]

    dx = trace[-1][0] - trace[0][0]
    dy = trace[-1][1] - trace[0][1]
    speeds = []
    directions = []

    for i in range(1, len(trace)):
        x1, y1 = trace[i-1]
        x2, y2 = trace[i]
        dist = np.linalg.norm([x2 - x1, y2 - y1])
        speeds.append(dist)
        directions.append(np.arctan2(y2 - y1, x2 - x1))

    avg_speed = np.mean(speeds)
    direction_changes = np.sum(np.abs(np.diff(directions)))
    return [dx, dy, avg_speed, direction_changes]

# ======== MAIN REAL-TIME TRACKING ========
cap = cv2.VideoCapture(0)  # یا 'video.mp4' برای فایل

bg_subtractor = cv2.createBackgroundSubtractorMOG2()
traces = {}
next_id = 0
ai = BehaviorAI()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    fgmask = bg_subtractor.apply(frame)
    contours, _ = cv2.findContours(fgmask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    current_positions = []

    for cnt in contours:
        if cv2.contourArea(cnt) < 500:
            continue

        x, y, w, h = cv2.boundingRect(cnt)
        cx, cy = x + w // 2, y + h // 2
        current_positions.append((cx, cy))
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    new_traces = {}
    matched_ids = set()

    for cx, cy in current_positions:
        min_dist = float('inf')
        matched_id = None
        for id, trace in traces.items():
            if len(trace) == 0:
                continue
            prev_x, prev_y = trace[-1]
            dist = np.linalg.norm([cx - prev_x, cy - prev_y])
            if dist < 50 and id not in matched_ids:
                min_dist = dist
                matched_id = id

        if matched_id is None:
            matched_id = next_id
            next_id += 1
            new_traces[matched_id] = []

        else:
            new_traces[matched_id] = traces[matched_id]

        new_traces[matched_id].append((cx, cy))
        matched_ids.add(matched_id)

    traces = new_traces

    for id, trace in traces.items():
        if len(trace) >= 2:
            for i in range(1, len(trace)):
                cv2.line(frame, trace[i-1], trace[i], (255, 0, 0), 2)

            features = extract_features(trace)
            behavior = ai.predict_behavior(features)

            if len(trace) >= 10:
                if features[2] < 2:
                    label = "Idle"
                elif features[3] > 4:
                    label = "Erratic"
                else:
                    label = "Normal"
                ai.learn_from(features, label)

            cv2.putText(frame, f"ID:{id} AI:{behavior}", trace[-1], cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

    cv2.imshow("Real-Time Tracker with AI", frame)
    if cv2.waitKey(1) == 27:  # ESC
        break

cap.release()
cv2.destroyAllWindows()
