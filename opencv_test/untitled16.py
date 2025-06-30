import cv2
import numpy as np
import torch

# AI-based Visual Memory
class ObjectMemory:
    def __init__(self):
        self.memory = {}  # object_id: feature_vector
        self.next_id = 1

    def extract_features(self, crop):
        try:
            crop_resized = cv2.resize(crop, (32, 32))  # Resize to fixed size
            crop_tensor = torch.tensor(crop_resized.transpose(2, 0, 1), dtype=torch.float32).unsqueeze(0) / 255.0
            return crop_tensor.view(-1)  # Flatten
        except:
            return None

    def memorize(self, crop):
        vec = self.extract_features(crop)
        if vec is None:
            return None
        obj_id = self.next_id
        self.memory[obj_id] = vec
        self.next_id += 1
        return obj_id

    def find_match(self, crop, threshold=0.95):
        vec = self.extract_features(crop)
        if vec is None:
            return None, 0.0

        best_id = None
        best_sim = 0.0
        for obj_id, stored_vec in self.memory.items():
            sim = torch.cosine_similarity(vec, stored_vec, dim=0).item()
            if sim > best_sim and sim > threshold:
                best_sim = sim
                best_id = obj_id

        return best_id, best_sim

# Video object tracker
def main():
    cap = cv2.VideoCapture(0)  # Use webcam; change to "video.mp4" for a file
    fgbg = cv2.createBackgroundSubtractorMOG2()
    memory = ObjectMemory()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        fgmask = fgbg.apply(frame)
        _, thresh = cv2.threshold(fgmask, 200, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for cnt in contours:
            if cv2.contourArea(cnt) < 800:
                continue

            x, y, w, h = cv2.boundingRect(cnt)
            crop = frame[y:y+h, x:x+w]

            match_id, sim = memory.find_match(crop)
            if match_id is not None:
                label = f"Seen before (ID {match_id})"
                color = (0, 255, 0)
            else:
                new_id = memory.memorize(crop)
                label = f"New Object (ID {new_id})"
                color = (255, 0, 0)

            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
                        0.6, (255, 255, 255), 2)

        cv2.imshow("Object Tracker with Memory", frame)
        if cv2.waitKey(1) & 0xFF == 27:  # ESC to quit
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
