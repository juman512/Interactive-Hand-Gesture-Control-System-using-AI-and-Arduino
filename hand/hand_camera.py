import cv2
import mediapipe as mp
import math
import serial
import time


# =========================================================
# Arduino
# =========================================================

arduino = serial.Serial("COM6", 9600)

# Give Arduino time to reset after opening Serial
time.sleep(2)


# =========================================================
# MediaPipe
# =========================================================

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
RunningMode = mp.tasks.vision.RunningMode


options = HandLandmarkerOptions(
    base_options=BaseOptions(
        model_asset_path="hand_landmarker.task"
    ),
    running_mode=RunningMode.VIDEO,
    num_hands=1,
    min_hand_detection_confidence=0.7,
    min_hand_presence_confidence=0.7,
    min_tracking_confidence=0.7
)


# =========================================================
# Calculate angle
# =========================================================

def calculate_angle(a, b, c):

    angle = math.degrees(
        math.atan2(c.y - b.y, c.x - b.x)
        -
        math.atan2(a.y - b.y, a.x - b.x)
    )

    angle = abs(angle)

    if angle > 180:
        angle = 360 - angle

    return angle


# =========================================================
# Detect fingers
# =========================================================

def get_fingers(hand):

    fingers = []

    # -----------------------------------------------------
    # Thumb
    # -----------------------------------------------------

    thumb_angle = calculate_angle(
        hand[2],
        hand[3],
        hand[4]
    )

    if thumb_angle > 155:
        fingers.append(1)
    else:
        fingers.append(0)


    # -----------------------------------------------------
    # Index
    # -----------------------------------------------------

    index_angle = calculate_angle(
        hand[5],
        hand[6],
        hand[8]
    )

    if index_angle > 155:
        fingers.append(1)
    else:
        fingers.append(0)


    # -----------------------------------------------------
    # Middle
    # -----------------------------------------------------

    middle_angle = calculate_angle(
        hand[9],
        hand[10],
        hand[12]
    )

    if middle_angle > 155:
        fingers.append(1)
    else:
        fingers.append(0)


    # -----------------------------------------------------
    # Ring
    # -----------------------------------------------------

    ring_angle = calculate_angle(
        hand[13],
        hand[14],
        hand[16]
    )

    if ring_angle > 155:
        fingers.append(1)
    else:
        fingers.append(0)


    # -----------------------------------------------------
    # Pinky
    # -----------------------------------------------------

    pinky_angle = calculate_angle(
        hand[17],
        hand[18],
        hand[20]
    )

    if pinky_angle > 155:
        fingers.append(1)
    else:
        fingers.append(0)


    return fingers


# =========================================================
# Draw hand
# =========================================================

def draw_hand(frame, hand):

    h, w, _ = frame.shape

    connections = [

        # Thumb
        (0, 1),
        (1, 2),
        (2, 3),
        (3, 4),

        # Index
        (0, 5),
        (5, 6),
        (6, 7),
        (7, 8),

        # Middle
        (5, 9),
        (9, 10),
        (10, 11),
        (11, 12),

        # Ring
        (9, 13),
        (13, 14),
        (14, 15),
        (15, 16),

        # Pinky
        (13, 17),
        (17, 18),
        (18, 19),
        (19, 20),

        # Palm
        (0, 17)
    ]


    # -----------------------------------------------------
    # Draw lines
    # -----------------------------------------------------

    for start, end in connections:

        x1 = w - int(hand[start].x * w)
        y1 = int(hand[start].y * h)

        x2 = w - int(hand[end].x * w)
        y2 = int(hand[end].y * h)

        cv2.line(
            frame,
            (x1, y1),
            (x2, y2),
            (0, 255, 0),
            2
        )


    # -----------------------------------------------------
    # Draw points
    # -----------------------------------------------------

    for landmark in hand:

        x = w - int(landmark.x * w)
        y = int(landmark.y * h)

        cv2.circle(
            frame,
            (x, y),
            6,
            (0, 255, 0),
            -1
        )


# =========================================================
# Camera
# =========================================================

cap = cv2.VideoCapture(0)


if not cap.isOpened():

    print("Couldn't open the camera!")

    arduino.close()

    exit()


# =========================================================
# Start MediaPipe
# =========================================================

with HandLandmarker.create_from_options(options) as landmarker:

    timestamp = 0

    while True:

        # -------------------------------------------------
        # Read camera
        # -------------------------------------------------

        success, frame = cap.read()

        if not success:

            print("Couldn't read the camera frame!")
            break


        # -------------------------------------------------
        # Original image for analysis
        # -------------------------------------------------

        original_frame = frame.copy()


        # -------------------------------------------------
        # BGR -> RGB
        # -------------------------------------------------

        rgb_frame = cv2.cvtColor(
            original_frame,
            cv2.COLOR_BGR2RGB
        )


        # -------------------------------------------------
        # MediaPipe image
        # -------------------------------------------------

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb_frame
        )


        # -------------------------------------------------
        # Timestamp
        # -------------------------------------------------

        timestamp += 1


        # -------------------------------------------------
        # Detect hand
        # -------------------------------------------------

        result = landmarker.detect_for_video(
            mp_image,
            timestamp
        )


        # =================================================
        # Mirror camera for display
        # =================================================

        display_frame = cv2.flip(
            original_frame,
            1
        )


        # =================================================
        # If hand detected
        # =================================================

        if result.hand_landmarks:

            hand = result.hand_landmarks[0]


            # -------------------------------------------------
            # Detect fingers
            # -------------------------------------------------

            fingers = get_fingers(hand)

            thumb = fingers[0]
            index = fingers[1]
            middle = fingers[2]
            ring = fingers[3]
            pinky = fingers[4]

            total = sum(fingers)


            # -------------------------------------------------
            # Handedness
            # -------------------------------------------------

            handedness = result.handedness[0][0].category_name


            # -------------------------------------------------
            # Send finger states to Arduino
            #
            # Example:
            # 10100
            #
            # Thumb  = 1
            # Index  = 0
            # Middle = 1
            # Ring   = 0
            # Pinky  = 0
            # -------------------------------------------------

            data = "".join(map(str, fingers))

            arduino.write(
                (data + "\n").encode()
            )


            # -------------------------------------------------
            # Draw hand
            # -------------------------------------------------

            draw_hand(
                display_frame,
                hand
            )


            # =================================================
            # Display information
            # =================================================

            cv2.putText(
                display_frame,
                f"Hand: {handedness}",
                (30, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2
            )


            cv2.putText(
                display_frame,
                f"Fingers: {total}",
                (30, 90),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.2,
                (0, 255, 0),
                3
            )


            cv2.putText(
                display_frame,
                f"T:{thumb} I:{index} M:{middle} R:{ring} P:{pinky}",
                (30, 130),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2
            )


            # -------------------------------------------------
            # Terminal output
            # -------------------------------------------------

            print(
                f"Hand: {handedness} | "
                f"Thumb: {thumb} | "
                f"Index: {index} | "
                f"Middle: {middle} | "
                f"Ring: {ring} | "
                f"Pinky: {pinky} | "
                f"Total: {total} | "
                f"Sent: {data}"
            )


        else:

            # -------------------------------------------------
            # No hand detected
            # Turn all LEDs OFF
            # -------------------------------------------------

            arduino.write(
                b"00000\n"
            )


        # =================================================
        # Show camera
        # =================================================

        cv2.imshow(
            "Hand Detection",
            display_frame
        )


        # =================================================
        # Q = Quit
        # =================================================

        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):

            break


# =========================================================
# Turn LEDs OFF before closing
# =========================================================

arduino.write(
    b"00000\n"
)

time.sleep(0.1)


# =========================================================
# Close
# =========================================================

arduino.close()

cap.release()

cv2.destroyAllWindows()