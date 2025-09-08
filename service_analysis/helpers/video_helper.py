import cv2
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import torch

def analyze_video(file_path: str, frame_interval=60):
    try:
        cap = cv2.VideoCapture(file_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # Model ve processor yükle
        model_name = "Salesforce/blip-image-captioning-base"
        processor = BlipProcessor.from_pretrained(model_name)
        model = BlipForConditionalGeneration.from_pretrained(model_name).to(
            "cuda" if torch.cuda.is_available() else "cpu"
        )

        results = []
        frame_id = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_id % frame_interval == 0:
                try:
                    # Frame'i direkt RAM üzerinden dönüştür
                    image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                    inputs = processor(images=image, return_tensors="pt")
                    inputs = {k: v.to(model.device) for k, v in inputs.items()}
                    out = model.generate(**inputs, max_new_tokens=50)
                    caption = processor.decode(out[0], skip_special_tokens=True)

                    results.append({"frame": frame_id, "caption": caption})
                except Exception as e:
                    results.append({"frame": frame_id, "caption": f"Error: {str(e)}"})
            
            frame_id += 1

        cap.release()
        return {
            "type": "video",
            "captions": results,
            "total_frames": total_frames,
            "status": "success"
        }
        
    except Exception as e:
        return {
            "type": "video",
            "error": f"Analysis failed: {str(e)}",
            "status": "error"
        }
