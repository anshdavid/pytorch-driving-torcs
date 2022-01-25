from src.vision.screengrab import ScreenGrab
import time
import cv2

instanceGrab = ScreenGrab()

while True:

    last_time = time.time()
    img = instanceGrab.GrabBGR()
    # print(img.shape)
    print("fps: {}".format(1 / (time.time() - last_time)))

    cv2.imshow("OpenCV/Numpy normal", img)
    # cv2.imshow("OpenCV/Numpy normal", cv2.cvtColor(img, cv2.COLOR_BGR2GRAY))

    if cv2.waitKey(25) & 0xFF == ord("q"):
        cv2.destroyAllWindows()
        break
