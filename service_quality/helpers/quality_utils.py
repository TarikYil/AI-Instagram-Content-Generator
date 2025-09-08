import os
from typing import Dict, Any
from PIL import Image

def validate_image_path(image_path: str) -> bool:
    """Image path'ini validate et"""
    
    if not os.path.exists(image_path):
        return False
    
    # Check if it's an image file
    valid_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff'}
    _, ext = os.path.splitext(image_path.lower())
    
    return ext in valid_extensions

def load_image_safely(image_path: str) -> Image.Image:
    """Image'i güvenli şekilde yükle"""
    
    if not validate_image_path(image_path):
        raise ValueError(f"Invalid image path: {image_path}")
    
    try:
        image = Image.open(image_path).convert('RGB')
        return image
    except Exception as e:
        raise ValueError(f"Failed to load image: {e}")

def interpret_quality_level(score: float) -> str:
    """Quality score'u level'a çevir"""
    
    if score >= 0.8:
        return "excellent"
    elif score >= 0.65:
        return "good"
    elif score >= 0.45:
        return "fair"
    else:
        return "poor"