import requests
import time
import base64
import os

BASE_URL = "http://127.0.0.1:8000/api/user/whatsapp"

def trigger_and_capture():
    print("1. Triggering Connect...")
    try:
        res = requests.post(f"{BASE_URL}/connect")
        print(f"Connect response: {res.json()}")
    except Exception as e:
        print(f"Connect failed: {e}")
        return

    print("2. Waiting for browser and QR (10s)...")
    time.sleep(10)

    print("3. Fetching QR Code...")
    try:
        res = requests.get(f"{BASE_URL}/qr")
        data = res.json()
        qr_data = data.get("qr")
        
        if qr_data and "base64," in qr_data:
            b64_str = qr_data.split("base64,")[1]
            img_data = base64.b64decode(b64_str)
            
            with open("manual_qr.png", "wb") as f:
                f.write(img_data)
            print("SUCCESS: QR Code saved to 'manual_qr.png'")
        else:
            print("FAIL: No QR code returned. Browser might be loading or locked.")
            print(f"Response: {data}")
            
    except Exception as e:
        print(f"QR Fetch failed: {e}")

if __name__ == "__main__":
    trigger_and_capture()
