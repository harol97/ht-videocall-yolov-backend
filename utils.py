from numpy import ndarray
from ultralytics import YOLO
from dataclasses import dataclass, Field

from detection import Detection
from point import Point
from rect import Rect

@dataclass
class Result:
    frame: ndarray
    detections: list[Detection]


class Tracker:
    model:YOLO | None = None

    def __init__(self):
        self.load_model()

    def load_model(self):
        if not self.model:
            self.model = YOLO("yolo26n.pt")


    def track(self, source: ndarray) -> Result:
        if not self.model:
            raise Exception("Model not loaded. Call load_model() first.")
        try:
            results = self.model.track(source, persist = True, verbose=False, classes=[0])
        except Exception as e:
            print(f"Error in model.track: {e}")
            return Result(frame=source, detections=[])
        frame = source
        detections = []
        for result in results:
            frame = result.plot()
            if result.boxes is None:
                continue
            if result.boxes.id is None:
                continue
            for box, track_id in zip(result.boxes.xyxy, result.boxes.id):
                x, y, x1, y1 = box
                point1 = Point(x=int(x), y=int(y))
                point2 = Point(x=int(x1), y=int(y1))
                detections.append(Detection(track_id=int(track_id), rect=Rect(point1=point1, point2=point2)))

        return Result(frame=frame, detections=detections)
