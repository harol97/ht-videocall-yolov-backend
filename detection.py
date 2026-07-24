from pydantic import BaseModel

from rect import Rect

class Detection(BaseModel):
    rect: Rect
    track_id: int

