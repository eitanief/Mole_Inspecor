import cv2
from datetime import datetime


class VideoCamera(object):

    CAPTURES_DIR = "static/captures/"

    def __init__(self):
        self.video = cv2.VideoCapture(0)

    def __del__(self):
        self.video.release()

    def get_frame(self):
        success, frame = self.video.read()
        return frame

    def get_feed(self):
        frame = self.get_frame()
        if frame is not None:
            ret, jpeg = cv2.imencode('.jpg', frame)
            return jpeg.tobytes()

    def capture(self):
        frame = self.get_frame()
        timestamp = datetime.now().strftime("%m-%d-%Y-%H-%M-%S")
        filename = VideoCamera.CAPTURES_DIR + timestamp + ".jpg"
        if not cv2.imwrite(filename, frame):
            raise RuntimeError("Unable to capture image " + timestamp)
        return timestamp