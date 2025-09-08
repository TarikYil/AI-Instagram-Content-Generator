from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import torch


def analyze_image(file_path: str):
    try:
        # Model ve processor yükle
        model_name = "Salesforce/blip-image-captioning-base"
        processor = BlipProcessor.from_pretrained(model_name)
        model = BlipForConditionalGeneration.from_pretrained(model_name).to(
            "cuda" if torch.cuda.is_available() else "cpu"
        )

        # Görüntüyü yükle
        image = Image.open(file_path).convert("RGB")

        # Caption üret - sizin verdiğiniz yapıyla aynı
        inputs = processor(images=image, return_tensors="pt").to(model.device)
        out = model.generate(**inputs)
        caption = processor.decode(out[0], skip_special_tokens=True)

        return {
            "type": "image", 
            "caption": caption,
            "status": "success"
        }
        
    except Exception as e:
        return {"type": "image", "caption": f"Analysis failed: {str(e)}", "status": "error"}
