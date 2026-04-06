import cv2
import numpy as np
import serial
import time

# --- 1. SETTINGS ---
PORT = 'COM5'
BAUD = 115200
TARGET_CLEAR = 125      
TARGET_TURBID = 90      
TURBID_THRESHOLD = 30   

# --- 2. INITIALIZATION ---
try:
    ser = serial.Serial(PORT, BAUD, timeout=1)
    time.sleep(2)
    print(f"Connected to {PORT}")
except:
    print("Serial Port not found. Running in Simulation Mode.")
    ser = None

cap = cv2.VideoCapture(1)

while True:
    ret, frame = cap.read()
    if not ret: break

    # --- 3. MEASUREMENTS ---
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    avg = np.mean(gray)
    sd = np.std(gray)  # Standard Deviation (Contrast)
    
    # --- 4. THE PRIORITY LOGIC ---
    
    if avg < 30:
        # SCENARIO A: TOO DARK (0-30)
        mode = "EXTREME DARK"
        led_value = 255
        color_ui = (0, 0, 255) # Red for Max Power
        
    elif avg > 230:
        # SCENARIO B: TOO BRIGHT (230+)
        mode = "OVEREXPOSED"
        led_value = 30 # Dropping below 50 as requested
        color_ui = (0, 255, 255) # Yellow
        
    else:
        # SCENARIO C: NORMAL OPERATION (30-230)
        # Now we check if the water is turbid or clear
        if sd < TURBID_THRESHOLD:
            mode = "TURBID WATER"
            target = TARGET_TURBID
            color_ui = (0, 165, 255) # Orange
        else:
            mode = "CLEAR WATER"
            target = TARGET_CLEAR
            color_ui = (0, 255, 0) # Green

        # Calculate error and adjust from middle baseline
        error = target - avg
        led_value = int(128 + (error * 0.8))
        
    # Final Safety Clamp
    led_value = max(0, min(255, led_value))

    # --- 5. OUTPUT & VISUALS ---
    if ser:
        ser.write(f"{led_value}\n".encode())

    # Print to console
    print(f"[{mode:15}] Avg: {avg:5.1f} | SD: {sd:5.1f} | PWM: {led_value}")

    # Visual Display
    cv2.putText(frame, f"MODE: {mode}", (20, 40), 1, 1.5, color_ui, 2)
    cv2.putText(frame, f"AVG BRIGHTNESS: {int(avg)}", (20, 75), 1, 1.2, (255,255,255), 1)
    cv2.putText(frame, f"CONTRAST (SD): {int(sd)}", (20, 105), 1, 1.2, (255,255,255), 1)
    cv2.putText(frame, f"PWM OUT: {led_value}", (20, 140), 1, 1.5, (0, 255, 255), 2)
    
    # Visual PWM Bar
    cv2.rectangle(frame, (20, 160), (20 + led_value, 180), color_ui, -1)
    cv2.rectangle(frame, (20, 160), (275, 180), (255, 255, 255), 1)

    cv2.imshow("Smart Underwater Light Controller", frame)

    if cv2.waitKey(1) & 0xFF == 27: # ESC to quit
        break

if ser: ser.close()
cap.release()
cv2.destroyAllWindows()