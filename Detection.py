
import numpy as np
import cv2
from threading import Thread
import utlis
from PIL import Image, ImageDraw, ImageFont
import requests
import time
import imutils
import websocket

ws = websocket.WebSocket()
####################################################

detect_obj = cv2.CascadeClassifier("trafficlight.xml")

useCamera = False
cameraNum = 0

videoPath = 0


frameWidth = 1270
frameHeight = 760

if useCamera:
    intialTracbarVals = [24, 55, 12, 100]  # wT,hT,wB,hB
else:
    intialTracbarVals = [42, 63, 14, 87]   # wT,hT,wB,hB
url = "http://192.168.0.2:8080/shot.jpg"
if useCamera:
    cap = cv2.VideoCapture(cameraNum)
    cap.set(3, frameWidth)
    cap.set(4, frameHeight)
else:
    cap = cv2.VideoCapture(videoPath)
count = 0
noOfArrayValues = 10
global arrayCurve, arrayCounter, directionText
averageCurve = 0
arrayCounter = 0
directionText = ''
arrayCurve = np.zeros([noOfArrayValues])
myVals = []
utlis.initializeTrackbars(intialTracbarVals)

car_cascade = cv2.CascadeClassifier('cars.xml')

ws.connect("ws://192.168.137.61:81")
while True:

    # success, img = cap.read()
    # img_resp = requests.get(url)
    # img_arr = np.array(bytearray(img_resp.content), dtype=np.uint8)
    # img = cv2.imdecode(img_arr, -1)
    # img = imutils.resize(img, width=frameWidth, height=frameHeight)
    success, img = cap.read()
    if success == True:
        if useCamera == False:
            img = cv2.resize(img, (frameWidth, frameHeight), None)
        imgWarpPoints = img.copy()
        imgFinal = img.copy()
        imgCanny = img.copy()

        imgUndis = utlis.undistort(img)
        imgThres, imgCanny, imgColor = utlis.thresholding(imgUndis)
        src = utlis.valTrackbars()
        imgWarp = utlis.perspective_warp(
            imgThres, dst_size=(frameWidth, frameHeight), src=src)
        imgWarpPoints = utlis.drawPoints(imgWarpPoints, src)
        imgSliding, curves, lanes, ploty = utlis.sliding_window(
            imgWarp, draw_windows=True)

        try:
            curverad = utlis.get_curve(imgFinal, curves[0], curves[1])
            lane_curve = np.mean([curverad[0], curverad[1]])
            imgFinal = utlis.draw_lanes(
                img, curves[0], curves[1], frameWidth, frameHeight, src=src)

            currentCurve = lane_curve // 50
            if int(np.sum(arrayCurve)) == 0:
                averageCurve = currentCurve
            else:
                averageCurve = np.sum(arrayCurve) // arrayCurve.shape[0]
            if abs(averageCurve-currentCurve) > 200:
                arrayCurve[arrayCounter] = averageCurve
            else:
                arrayCurve[arrayCounter] = currentCurve
            arrayCounter += 1
            if arrayCounter >= noOfArrayValues:
                arrayCounter = 0

            cv2.putText(imgFinal, str(int(averageCurve)), (20, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2, cv2.LINE_AA)

            directionText = 'D'
            if averageCurve > 10:
                directionText = 'RIGHT'

            elif averageCurve < -10:
                directionText = 'LEFT'

            elif averageCurve < 10 and averageCurve > -10:
                directionText = 'ALONG'

            elif averageCurve == -1000000:
                directionText = 'D'
            ws.send(directionText)
        except:
            lane_curve = 00
            pass

        font = ImageFont.truetype('TP_Kubua.ttf', 45)
        img_pil = Image.fromarray(imgFinal)
        draw = ImageDraw.Draw(img_pil)
        draw.text((20, 30), directionText, font=font, fill=(0, 255, 255))
        imgFinal = np.array(img_pil)

        # แสดง Lane Curve Lines
        imgFinal = utlis.drawLines(imgFinal,lane_curve)

        imgThres = cv2.cvtColor(imgThres, cv2.COLOR_GRAY2BGR)
        imgBlank = np.zeros_like(img)
        imgStacked = utlis.stackImages(0.7, ([img, imgUndis, imgWarpPoints],
                                            [imgColor, imgCanny, imgThres],
                                            [imgWarp, imgSliding, imgFinal]
                                            ))

        # แสดงขั้นตอน
        # cv2.imshow("PipeLine",imgStacked)
        cv2.resize(imgFinal, (500, 500), None)
        gray = cv2.cvtColor(imgFinal, cv2.COLOR_BGR2GRAY)
        cars = car_cascade.detectMultiScale(gray, 4, 1)
        for (x,y,w,h) in cars:
            cv2.rectangle(imgFinal,(x,y),(x+w,y+h),(0,0,255),2)
 
        # Display frames in a window 
        cv2.imshow("Result", imgFinal)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


cap.release()
cv2.destroyAllWindows()
