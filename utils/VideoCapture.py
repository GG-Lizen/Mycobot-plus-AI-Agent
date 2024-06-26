"""
@Time    : 2024/6/5 17:25
@Author  : GG-Lizen
@File    : VideoCapture.py
"""
import cv2
import threading


# bufferless VideoCapture
# class VideoCapture_Bufferless:
#     def __init__(self, name):
#         self.cap = cv2.VideoCapture(name)
#         self.lock = threading.Lock()
#         self.running = True
#         self.t = threading.Thread(target=self._reader)
#         self.t.daemon = True
#         self.t.start()

#     # grab frames as soon as they are available
#     def _reader(self):
#         while self.running:
#             with self.lock:
#                 ret = self.cap.grab()
#             if not ret:
#                 break

#     # retrieve latest frame
#     def read(self):
#         with self.lock:
#             ret, frame = self.cap.retrieve()
#         if not ret:
#             return None
#         return frame

#     # release the video capture and stop the thread
#     def release(self):
#         self.running = False
#         self.t.join()  # Wait for the thread to finish
#         with self.lock:
#             self.cap.release()
import cv2
import threading

class VideoCapture_Bufferless:
    def __init__(self, name):
        self.cap = cv2.VideoCapture(name)
        self.lock = threading.Lock()
        self.running = True
        self.frame = None
        self.t = threading.Thread(target=self._reader)
        self.t.daemon = True
        self.t.start()

    # grab frames as soon as they are available
    def _reader(self):
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                continue
            with self.lock:
                self.frame = frame

    # retrieve latest frame
    def read(self):
        with self.lock:
            frame = self.frame
        return frame

    # release the video capture and stop the thread
    def release(self):
        self.running = False
        self.t.join()  # Wait for the thread to finish
        self.cap.release()
