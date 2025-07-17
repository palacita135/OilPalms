from ultralytics import YOLO

def main():
    # Load YOLOv8 model
    model = YOLO('yolov8l.yaml')

    # Train the model
    model.train(
        data='C:/Users/palac/Documents/OilPalms/datasets/roboflow/data.yaml',
        epochs=150,
        imgsz=1280,
        batch=8,
        device='cpu'  # Use CPU since CUDA is not available
    )

if __name__ == '__main__':
    import multiprocessing
    multiprocessing.freeze_support()
    main()
