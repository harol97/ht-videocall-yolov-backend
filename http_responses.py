from pydantic import BaseModel, Field

class OfferBody(BaseModel):
    sdp: str
    offer_type: str = Field(alias="type")

    model_config = {"populate_by_name": True}

