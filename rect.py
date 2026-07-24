from pydantic import BaseModel

from point import Point


class Rect(BaseModel):
    point1: Point
    point2: Point
