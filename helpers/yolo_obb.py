import cv2
import numpy as np
from ultralytics import YOLO


def run_yolo_and_get_neck_and_nut(image, model_path):
    # Load the YOLO model
    model = YOLO(model_path)

    # Perform object detection
    results = model.predict(image, show=False, imgsz=640)  # device="mps" gives worse performance

    # Initialize variables to track the highest confidence for neck and nut
    best_neck = None
    best_nut = None
    best_neck_confidence = 0
    best_nut_confidence = 0

    # Loop through each detected object to find neck and nut with highest confidence
    for result in results[0].obb:
        cls = int(result.cls)  # Class ID
        class_name = results[0].names[cls]  # Class name
        confidence = result.conf[0]  # Confidence score

        # If the class is 'neck', keep track of the highest confidence
        if class_name == "neck" and confidence > best_neck_confidence:
            best_neck = result
            best_neck_confidence = confidence

        # If the class is 'nut', keep track of the highest confidence
        elif class_name == "nut" and confidence > best_nut_confidence:
            best_nut = result
            best_nut_confidence = confidence

    return best_neck, best_nut, results[0].names
