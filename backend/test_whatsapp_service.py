from app.services.whatsapp_service import whatsapp_service
import time
import base64

def test_qr():
    print("Testing WhatsApp Service...")
    
    # 1. Start Browser
    print("Starting browser...")
    success = whatsapp_service.start_browser()
    if not success:
        print("Failed to start browser.")
        return

    print("Browser started. Waiting for page load...")
    time.sleep(5)

    # 2. Get QR
    print("Fetching QR Code...")
    qr_b64 = whatsapp_service.get_qr_code()
    
    if qr_b64:
        print(f"QR Code fetched successfully! Length: {len(qr_b64)}")
        # Save to file to verify
        with open("test_qr.png", "wb") as f:
            f.write(base64.b64decode(qr_b64))
        print("Saved test_qr.png")
    else:
        print("Failed to fetch QR Code (None returned).")

    # 3. Cleanup
    print("Closing browser...")
    whatsapp_service.close()
    print("Done.")

if __name__ == "__main__":
    test_qr()
