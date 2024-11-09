from picamera2 import Picamera2

picam2 = Picamera2()

# Take Photos
picam2.start_and_capture_file("test.jpg")

# Take Movies
#picam2.start_and_record_video("test.mp4", duration=5)