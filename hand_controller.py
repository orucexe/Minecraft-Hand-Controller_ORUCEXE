import cv2
import mediapipe
import keyboard
import time


all_keys = ['w','a','s','d','space','shift','ctrl']
camera = None
mpHands = mediapipe.solutions.hands
hands = mpHands.Hands()
mpDraw = mediapipe.solutions.drawing_utils

ctrlFlag = False
inScreen = False

def set_camera(source): # Initialize or switch camera source
    global camera
    if camera is not None:
        camera.release()
    camera = cv2.VideoCapture(source)
    if not camera.isOpened():
        print(f"Failed to open camera source: {source}")

def process_frame(draw_lines=True, draw_numbers=False): # Process each frame from camera and detect hand gestures
    global ctrlFlag, inScreen, camera
    if camera is None or not camera.isOpened():
        return None, ""

    success, img = camera.read()
    if not success:
        return None, ""

    img = cv2.flip(img, 1)
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    hlms = hands.process(imgRGB)
    height, width, channels = img.shape

    INF = 10**9
    minYwithout0 = INF
    minXwithout0 = INF
    maxYwithout0 = -INF
    maxXwithout0 = -INF
    minYwithout8 = INF
    maxXwithout4 = -INF
    x0 = y0 = y8 = x4 = y13 = y14 = y20 = 0
    text = ""


    if hlms.multi_hand_landmarks:
        inScreen = True
        isLeft = True
        for handlandmarks, handedness in zip(hlms.multi_hand_landmarks, hlms.multi_handedness):
            label = handedness.classification[0].label

            if label != "Left":
                isLeft = False
                continue

            # Draw hand skeleton
            if draw_lines:
                connection_style = mpDraw.DrawingSpec(color=(255, 255, 255), thickness=2)
                landmark_style = mpDraw.DrawingSpec(color=(255, 0, 0), thickness=-1, circle_radius=4)

                mpDraw.draw_landmarks(
                    img,
                    handlandmarks,
                    mpHands.HAND_CONNECTIONS,
                    landmark_style,
                    connection_style
                )

            for fingerNum, landmark in enumerate(handlandmarks.landmark):
                positionX = int(landmark.x * width)
                positionY = int(landmark.y * height)

                # Draw Landmark numbers
                if draw_numbers:
                    cv2.putText(img, str(fingerNum), (positionX, positionY),cv2.FONT_HERSHEY_PLAIN , 1.8,  (0, 0, 255))

                if fingerNum == 13: y13 = positionY
                if fingerNum == 14: y14 = positionY
                if fingerNum == 20: y20 = positionY
                if fingerNum == 8: y8 = positionY
                else: minYwithout8 = min(minYwithout8, positionY)

                if fingerNum == 4: x4 = positionX
                else: maxXwithout4 = max(maxXwithout4, positionX)

                if fingerNum != 0:
                    minXwithout0 = min(minXwithout0, positionX)
                    minYwithout0 = min(minYwithout0, positionY)
                    maxXwithout0 = max(maxXwithout0, positionX)
                    maxYwithout0 = max(maxYwithout0, positionY)
                else:
                    x0 = positionX
                    y0 = positionY



        if isLeft == False:
            return img, ''

        # Forward movement (W key)
        if y0 > maxYwithout0:
            if y8 > minYwithout8:
                if ctrlFlag:
                    keyboard.release('w')
                    time.sleep(0.1)
                ctrlFlag = False
            keyboard.press('w')
            text = 'Forward'
            # Chrouching with shift
            if y20 < y13:
                keyboard.press('shift')
                if len(text) > 0:
                    text += " + Shift"
                else:
                    text = "Shift"
            else: keyboard.release('shift')
        else:
            keyboard.release('w')

        # Run
        if y0 > maxYwithout0 and y8 < minYwithout8:
            if ctrlFlag == False:
                keyboard.press('ctrl')
                time.sleep(0.1)
                keyboard.release('ctrl')
                ctrlFlag = True
            text = 'Run'

        # Move left (A key)
        if x0 > maxXwithout0:
            keyboard.press('a')
            text = "Left"
            # Chrouching with shift
            if y20 < y13:
                keyboard.press('shift')
                if len(text) > 0:
                    text += " + Shift"
                else:
                    text = "Shift"
            else: keyboard.release('shift')
        else:
            keyboard.release('a')

        # Move right (D key)
        if x0 < minXwithout0:
            keyboard.press('d')
            text = "Right"
            # Chrouching with shift
            if y20 < y13:
                keyboard.press('shift')
                if len(text) > 0:
                    text += " + Shift"
                else:
                    text = "Shift"
            else: keyboard.release('shift')
        else:
            keyboard.release('d')

        # Move backward (S key)
        if y0 < minYwithout0:
            keyboard.press('s')
            text = "Backward"
            # Chrouching with shift
            if y20 > y14:
                keyboard.press('shift')
                if len(text) > 0:
                    text += " + Shift"
                else:
                    text = "Shift"
            else: keyboard.release('shift')
        else:
            keyboard.release('s')

        # Jump (Space key)
        if x4 > maxXwithout4:
            keyboard.press('space')
            if len(text) > 0:
                text += " Jump"
            else:
                text = "Jump"
        else:
            keyboard.release('space')


    else:
        # If hand leaves screen, release all keys
        if inScreen:
            for key in all_keys:
                keyboard.release(key)
            inScreen = False

    return img, text
