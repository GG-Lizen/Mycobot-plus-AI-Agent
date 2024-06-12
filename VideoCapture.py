import cv2
import threading


# bufferless VideoCapture
class VideoCapture_Bufferless:
    def __init__(self, name):
        self.cap = cv2.VideoCapture(name)
        self.lock = threading.Lock()
        self.running = True
        self.t = threading.Thread(target=self._reader)
        self.t.daemon = True
        self.t.start()

    # grab frames as soon as they are available
    def _reader(self):
        while self.running:
            with self.lock:
                ret = self.cap.grab()
            if not ret:
                break

    # retrieve latest frame
    def read(self):
        with self.lock:
            ret, frame = self.cap.retrieve()
        if not ret:
            return None
        return frame

    # release the video capture and stop the thread
    def release(self):
        self.running = False
        self.t.join()  # Wait for the thread to finish
        with self.lock:
            self.cap.release()
