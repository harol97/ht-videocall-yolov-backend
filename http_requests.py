from pydantic import BaseModel


class OfferBody(BaseModel):
    sdp: str
    type: str
