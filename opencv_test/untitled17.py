import cv2
import numpy as np
import torch
import torchvision.transforms as transforms
from torchvision.models import resnet18
from torch.nn.functional import cosine_similarity

# Use GPU if available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Feature extractor using pretrained ResNet18
class VisualFeatureExtractor:
    def __init__(self):
        model = resnet18(pretrained=True)
        self.model = torch.nn.Sequential(*list(model.children())[:-1]).to(device).eval()
        self.transform = transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize((224, 224)),
            transforms.ToTensor()
        ])

    def extract(self, image):
        try:
            tensor = self.transform(image).unsqueeze(0).to(device)
            with torch.no_grad():
                features = self.model(tensor).squeeze()
            return features / features.norm()
        except:
            return None

# Memory system for object identity
class ObjectMemory:
    def __init__(self):
        self.memory = {}  # id: feature_vector
        self.next_id = 1

    def compare(self, feat, threshold=0.9):
        best_id, best_sim = None, 0.0
        for obj_id, stored_feat in self.memory.items():
            sim = cosine_similarity(feat, stored_feat, dim=0).item()
            if sim > best_sim and sim > threshold:
                best_id, best_sim = obj_id, sim
        return best_id, best_sim

    def memorize(self, feat):
        obj_id = self.next_id
        self.memory[obj_id] = feat
        self.next_id += 1
        return obj_id

# Main application
def main():
    cap = cv2.VideoCapture(0)
    fgbg = cv2.createBackgroundSubtractorMOG2()
    extractor = VisualFeatureExtractor()
    memory = ObjectMemory()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        fgmask = fgbg.apply(frame)
        _, thresh = cv2.threshold(fgmask, 200, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for cnt in contours:
            if cv2.contourArea(cnt) < 1000:
                continue

            x, y, w, h = cv2.boundingRect(cnt)
            crop = frame[y:y+h, x:x+w]
            feat = extractor.extract(crop)

            if feat is None:
                continue

            matched_id, similarity = memory.compare(feat)

            if matched_id is not None:
                label = f"Known ID {matched_id} ({similarity*100:.1f}%)"
                color = (0, 255, 0)
            else:
                new_id = memory.memorize(feat)
                label = f"New Object (ID {new_id})"
                color = (0, 0, 255)

            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
            cv2.putText(frame, label, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX,
                        0.6, (255, 255, 255), 2)

        cv2.imshow("AI Object Memory", frame)
        if cv2.waitKey(1) & 0xFF == 27:  # ESC
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
