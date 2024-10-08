from picamera2 import Picamera2
import cv2

picam2 = Picamera2()

# Take photos
picam2.start_and_capture_file("test.jpg")

# Take movies
picam2.start_and_record_video("test.mp4", duration=5)
