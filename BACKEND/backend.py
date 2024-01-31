import cv2
import mediapipe as mp
import pyautogui
import subprocess
import speech_recognition as sr
import time

listener = sr.Recognizer()


cap = cv2.VideoCapture(0)
hand_detector = mp.solutions.hands.Hands()
drawing_utils = mp.solutions.drawing_utils
screen_width, screen_height = pyautogui.size()
right_hand_index_y = 0
left_hand_index_x = 0
left_hand_index_y = 0

def count_fingers(lst):
    cnt = 0
    thresh = (lst.landmark[0].y * 100 - lst.landmark[9].y * 100) / 2

    if (lst.landmark[5].y * 100 - lst.landmark[8].y * 100) > thresh:
        cnt += 1

    if (lst.landmark[9].y * 100 - lst.landmark[12].y * 100) > thresh:
        cnt += 1

    if (lst.landmark[13].y * 100 - lst.landmark[16].y * 100) > thresh:
        cnt += 1

    if (lst.landmark[17].y * 100 - lst.landmark[20].y * 100) > thresh:
        cnt += 1

    if (lst.landmark[5].x * 100 - lst.landmark[4].x * 100) > 6:
        cnt += 1

    return cnt

prev = -1
start_time = time.time()

while True:
    _, frame = cap.read()
    frame = cv2.flip(frame, 1)
    frame_height, frame_width, _ = frame.shape
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    output = hand_detector.process(rgb_frame)
    hands = output.multi_hand_landmarks
    if hands:
        for hand in hands:
            drawing_utils.draw_landmarks(frame, hand)
            landmarks = hand.landmark
            for id, landmark in enumerate(landmarks):
                x = int(landmark.x * frame_width)
                y = int(landmark.y * frame_height)
                if id == 8 and hand == hands[0]:  # Right Hand
                    cv2.circle(img=frame, center=(x, y), radius=10, color=(0, 255, 255))
                    right_hand_index_y = screen_height / frame_height * y

                elif id == 8 and hand == hands[1]:  # Left Hand
                    cv2.circle(img=frame, center=(x, y), radius=10, color=(0, 255, 255))
                    left_hand_index_x = screen_width / frame_width * x
                    left_hand_index_y = screen_height / frame_height * y

                    if abs(right_hand_index_y - left_hand_index_y) < 20:
                        pyautogui.click()
                        pyautogui.sleep(1)
                    elif abs(right_hand_index_y - left_hand_index_y) < 100:
                        pyautogui.moveTo(left_hand_index_x, left_hand_index_y)

    res = hand_detector.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

    if res.multi_hand_landmarks:
        hand_keyPoints = res.multi_hand_landmarks[0]

        cnt = count_fingers(hand_keyPoints)

        if not (prev == cnt):
            if (time.time() - start_time) > 0.2:
                if cnt == 1:
                    pyautogui.hotkey('volumeup')
                elif cnt == 2:
                    pyautogui.hotkey('volumedown')

                start_time = time.time()
                prev = cnt

        drawing_utils.draw_landmarks(frame, hand_keyPoints, mp.solutions.hands.HAND_CONNECTIONS)

    cv2.imshow('Virtual Mouse and Volume Control', frame)

    if cv2.waitKey(1) == 27:
        cv2.destroyAllWindows()
        cap.release()
        break
