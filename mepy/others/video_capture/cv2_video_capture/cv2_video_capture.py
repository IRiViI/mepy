# camera.py

# import cv2

class VideoCapture(object):
    def __init__(self):
        pass
        # self.video = cv2.VideoCapture(0)
    
    def __del__(self):
        pass
        # self.video.release()
    
    def get_frame(self):
        pass
        # success, image = self.video.read()
        # ret, jpeg = cv2.imencode('.jpg', image)
        # return jpeg.tobytes()