from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..services.whatsapp_service import whatsapp_service
import base64

router = APIRouter()

@router.get("/status")
def get_status():
    is_connected = whatsapp_service.is_logged_in()
    return {"connected": is_connected}

@router.post("/connect")
def connect_whatsapp():
    if whatsapp_service.is_logged_in():
        return {"message": "Already connected", "connected": True}
    
    success = whatsapp_service.start_browser()
    if not success:
        raise HTTPException(status_code=500, detail="Failed to start browser")
    
    return {"message": "Browser started. Please scan QR code on the host machine.", "connected": False}

@router.post("/disconnect")
def disconnect_whatsapp():
    whatsapp_service.close()
    return {"message": "Disconnected", "connected": False}

@router.get("/qr")
def get_qr():
    qr_base64 = whatsapp_service.get_qr_code()
    if qr_base64:
        return {"qr": f"data:image/png;base64,{qr_base64}"}
    return {"qr": None}

class PhoneNumber(BaseModel):
    phone: str

@router.post("/pair")
def pair_device(data: PhoneNumber):
    code = whatsapp_service.get_pairing_code(data.phone)
    if code:
        return {"code": code}
    raise HTTPException(status_code=400, detail="Kod alınamadı")

@router.get("/groups")
def get_whatsapp_groups():
    if not whatsapp_service.is_logged_in():
        raise HTTPException(status_code=400, detail="WhatsApp bağlı değil")
    
    chats = whatsapp_service.get_chats()
    return {"groups": chats}

@router.post("/logout")
def logout_whatsapp():
    whatsapp_service.logout()
    return {"message": "Logged out"}
