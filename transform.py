from aiortc.mediastreams import VideoStreamTrack
from av.video.frame import VideoFrame
from utils import Tracker
import asyncio
from deepface import DeepFace


class VideoTransformTrack(VideoStreamTrack):
    """
    A video stream track that transforms frames from an another track.
    """

    kind = "video"

    def __init__(self, track):
        super().__init__()
        self.track = track
        self.tracker = Tracker()
        self.input_queue = asyncio.Queue(maxsize=1)
        self.last_result = None

        self.processing_task = asyncio.create_task(
            self.process_frames()
        )

    async def close_stream(self):
        self.processing_task.cancel()
        asyncio.gather(self.processing_task)

    async def process_frames(self):
        while True:
            try:
                frame = await self.input_queue.get()

                image = frame.to_ndarray(
                    format="bgr24"
                )

                result = self.tracker.track(image)

                new_frame = VideoFrame.from_ndarray(
                    result.frame,
                    format="bgr24"
                )

                new_frame.pts = frame.pts
                new_frame.time_base = frame.time_base

                self.last_result = new_frame
            except asyncio.CancelledError:
                print("processing task has been cencelled")
                raise


    async def recv(self):
        frame = await self.track.recv()

        if self.input_queue.full():
            self.input_queue.get
            try:
                self.input_queue.get_nowait()
            except asyncio.QueueEmpty:
                pass

        await self.input_queue.put(frame)

        if self.last_result:
            self.last_result.pts = frame.pts
            self.last_result.time_base = frame.time_base
            return self.last_result

        return frame
