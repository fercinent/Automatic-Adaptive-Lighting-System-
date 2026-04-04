import cv2
import numpy as np
import serial
import time

# 🔌 Change COM port
ser = serial.Serial('COM5', 115200)
time.sleep(2)

cap = cv2.VideoCapture(1)

target = 120

while True:
    ret, frame = cap.read()

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    brightness = np.mean(gray)

    error = target - brightness
    led_value = int(128 + error)
    led_value = max(0, min(255, led_value))

    # Send PWM value
    ser.write(f"{led_value}\n".encode())

    print("Brightness:", brightness, "LED PWM:", led_value)

    cv2.imshow("Camera", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()