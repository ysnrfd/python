import cv2
import numpy as np
import torch
import torchvision.transforms as transforms
from torchvision.models import mobilenet_v2
from torch.nn.functional import cosine_similarity

# Use GPU if available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Lightweight feature extractor using MobileNetV2
class FastFeatureExtractor:
    def __init__(self):
        model = mobilenet_v2(pretrained=True).features
        self.model = torch.nn.Sequential(*list(model.children())[:-1]).to(device).eval()
        self.transform = transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize((96, 96)),
            transforms.ToTensor()
        ])

    def extract(self, image):
        try:
            tensor = self.transform(image).unsqueeze(0).to(device)
            with torch.no_grad():
                feat = self.model(tensor).mean([2, 3]).squeeze()
            return feat / feat.norm()
        except:
            return None

# Simple memory with similarity threshold
class ObjectMemory:
    def __init__(self, threshold=0.88):
        self.memory = {}
        self.next_id = 1
        self.threshold = threshold

    def match(self, feat):
        best_id, best_sim = None, 0.0
        for obj_id, ref_feat in self.memory.items():
            sim = cosine_similarity(feat, ref_feat, dim=0).item()
            if sim > best_sim and sim > self.threshold:
                best_id, best_sim = obj_id, sim
        return best_id, best_sim

    def add(self, feat):
        obj_id = self.next_id
        self.memory[obj_id] = feat
        self.next_id += 1
        return obj_id

# Main app
def main():
    cap = cv2.VideoCapture(0)
    fgbg = cv2.createBackgroundSubtractorMOG2()
    extractor = FastFeatureExtractor()
    memory = ObjectMemory()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        fg = fgbg.apply(frame)
        _, thresh = cv2.threshold(fg, 200, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for cnt in contours:
            if cv2.contourArea(cnt) < 1200:
                continue

            x, y, w, h = cv2.boundingRect(cnt)
            roi = frame[y:y+h, x:x+w]
            feat = extractor.extract(roi)

            if feat is None:
                continue

            matched_id, similarity = memory.match(feat)
            if matched_id:
                label = f"Known #{matched_id} ({similarity*100:.1f}%)"
                color = (0, 255, 0)
            else:
                new_id = memory.add(feat)
                label = f"New Object #{new_id}"
                color = (0, 0, 255)

            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
            cv2.putText(frame, label, (x, y-8), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        cv2.imshow("Fast Object Understanding", frame)
        if cv2.waitKey(1) & 0xFF == 27:  # ESC to exit
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
