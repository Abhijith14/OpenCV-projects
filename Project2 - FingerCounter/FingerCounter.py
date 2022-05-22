import mediapipe as mp
import cv2
import time


pTime = 0
mp_drawing = mp.solutions.drawing_utils
mp_holistic = mp.solutions.holistic

cap = cv2.VideoCapture(0)

################################
wCam, hCam = 1280, 960
################################

cap.set(3, wCam)
cap.set(4, hCam)

tipIds = [4, 8, 12, 16, 20]

def set_color(color, t, r): # color - BGR, thickness, circle_radius
    return mp_drawing.DrawingSpec(color=color, thickness=t, circle_radius=r)


def fingersUp(lmList, hand):
        fingers = []

        if hand == 0:  # left hand
            fingers.append(0)  # denoting left hand
            # Thumb
            if lmList[tipIds[0]].x > lmList[tipIds[0] - 1].x:
                fingers.append(1)
            else:
                fingers.append(0)
        elif hand == 1:  # right hand
            fingers.append(1)  # denoting right hand
            # Thumb
            if lmList[tipIds[0]].x > lmList[tipIds[0] - 1].x:
                fingers.append(0)
            else:
                fingers.append(1)

        # 4 Fingers
        for id in range(1, 5):
            if lmList[tipIds[id]].y < lmList[tipIds[id] - 2].y:
                fingers.append(1)
            else:
                fingers.append(0)

        return fingers


def detection_start():
    global pTime
    # Initiate holistic model
    with mp_holistic.Holistic(min_detection_confidence=0.7, min_tracking_confidence=0.7) as holistic:
        while cap.isOpened():
            ret, frame = cap.read()
            frame = cv2.flip(frame, 1)

            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = holistic.process(image)
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            mp_drawing.draw_landmarks(image, results.face_landmarks, mp_holistic.FACEMESH_CONTOURS,
                                      set_color((80, 110, 10), 1, 1),
                                      set_color((80, 256, 121), 1, 1))
            mp_drawing.draw_landmarks(image, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS,
                                      set_color((121, 22, 76), 2, 4),
                                      set_color((121, 44, 250), 2, 2))
            mp_drawing.draw_landmarks(image, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS,
                                      set_color((121, 22, 76), 2, 4),
                                      set_color((121, 44, 250), 2, 2))
            mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS,
                                      set_color((245, 117, 66), 2, 4),
                                      set_color((245, 66, 230), 2, 2))

            Fcount = 0
            # Start counting
            if results.left_hand_landmarks is not None:
                raised_lfingers = fingersUp(results.left_hand_landmarks.landmark, 1)
                Fcount = Fcount + raised_lfingers.count(1) - 1

            if results.right_hand_landmarks is not None:
                raised_rfingers = fingersUp(results.right_hand_landmarks.landmark, 0)
                Fcount = Fcount + raised_rfingers.count(1)

            cv2.rectangle(image, (20, 225), (170, 425), (0, 255, 0), cv2.FILLED)

            if Fcount < 10:
                size = 5
            else:
                size = 3

            cv2.putText(image, str(Fcount), (40, 375), cv2.FONT_HERSHEY_COMPLEX,
                    size, (255, 0, 0), 25)

            # FPS CODE
            cTime = time.time()
            fps = 1 / (cTime - pTime)
            pTime = cTime
            cv2.putText(image, f'FPS: {int(fps)}', (40, 50), cv2.FONT_HERSHEY_COMPLEX,
                        1, (255, 0, 0), 3)

            cv2.imshow("Img", image)
            cv2.waitKey(1)


if __name__ == '__main__':
    detection_start()
