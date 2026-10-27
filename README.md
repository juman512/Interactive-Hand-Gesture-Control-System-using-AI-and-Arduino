# Interactive-Hand-Gesture-Control-System-using-AI-and-Arduino

Project Title:
Interactive Hand Gesture Control System Using Computer Vision and Arduino

Project Overview & Description:
An interactive embedded systems project that utilizes Artificial Intelligence and Computer Vision to bridge software with hardware. The system captures video frames through the laptop's built-in webcam, processes hand landmarks in real-time using Python, OpenCV, and MediaPipe, and tracks the status of each finger (Thumb, Index, Middle, Ring, and Pinky). 

Through Serial Communication, the detected finger states are sent instantly to an Arduino microcontroller. In response, the hardware dynamically controls a set of LEDs and a buzzer to produce specific musical tones corresponding to the raised fingers.

Key Features & Technologies Used:
- Programming Languages: Python, C++ (Arduino IDE)
- Libraries & Frameworks: MediaPipe (Hand Landmarker model), OpenCV, PySerial
- Hardware Components: Laptop Built-in Webcam, Arduino Board, LEDs, Piezo Buzzer
- Core Functionality: Real-time hand tracking, angle calculation for finger detection, and bidirectional serial communication between Python and Arduino.
