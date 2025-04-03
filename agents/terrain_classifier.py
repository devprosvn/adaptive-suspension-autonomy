import torch

class MobileViTClassifier:
    def __init__(self, model_path: str):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = torch.load(model_path, map_location=self.device)
        self.model.eval()
        self.model = self.model.to(self.device).half()

    def predict_class(self, tensor_img: torch.Tensor) -> int:
        with torch.no_grad():
            outputs = self.model(tensor_img.to(self.device).half())
            return torch.argmax(outputs, dim=1).item()

# Example usage
classifier = MobileViTClassifier(model_path="models/mobilevit_fp16.pt")