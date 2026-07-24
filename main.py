from contextlib import asynccontextmanager
from uuid import uuid4

from aiortc import RTCPeerConnection, RTCSessionDescription
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from torch.cuda import is_available

from http_requests import OfferBody
import http_responses
from transform import VideoTransformTrack

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[TORCH] CUDA is available: ", is_available())
    yield

app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="templates"), name="static")
origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return HTMLResponse(open("templates/index.html").read());

pcs: set[RTCPeerConnection] = set()

@app.post("/offer", response_model=http_responses.OfferBody)
async def offer(body: OfferBody):
    offer = RTCSessionDescription(sdp=body.sdp, type=body.type)
    pc = RTCPeerConnection()
    pc_id = "PeerConnection(%s)" % uuid4()
    pcs.add(pc)
    transform: VideoTransformTrack | None = None

    @pc.on("connectionstatechange")
    async def on_connectionstatechange() -> None:
        nonlocal transform
        print("Connection state is %s" % pc.connectionState)
        if pc.connectionState in ["failed", "closed", "disconnected"]:
            if transform:
                await transform.close_stream()
            del transform
            await pc.close()
            pcs.discard(pc)

    @pc.on("track")
    def on_track(track):
        nonlocal transform
        if track.kind == "video":
            transform = VideoTransformTrack(track)
            pc.addTrack(transform)
    
    await pc.setRemoteDescription(offer)
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return dict(sdp=pc.localDescription.sdp, offer_type=pc.localDescription.type)
