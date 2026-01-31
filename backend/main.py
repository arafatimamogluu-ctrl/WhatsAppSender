from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from app.database import create_db_and_tables
from app.routers import auth, management, whatsapp, user_routes, admin_routes

app = FastAPI(title="Otonom Toplu Mesajlaşma SaaS", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Router'ları bağla
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(management.router, prefix="/api/manage", tags=["Yönetim"])
app.include_router(whatsapp.router, prefix="/api/user/whatsapp", tags=["WhatsApp"])
app.include_router(user_routes.router, prefix="/api/user", tags=["Kullanıcı Dashboard"])
app.include_router(admin_routes.router, prefix="/api/admin", tags=["Admin Dashboard"])

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    
    # Pre-warm WhatsApp Browser for instant QR Code
    from app.services.whatsapp_service import whatsapp_service
    whatsapp_service.start_browser()
    import time
    time.sleep(5) # Allow browser to warm up in headless mode
    
    # Scheduler'ı burada başlatacağız ileride
    # from app.services.scheduler import start_scheduler
    # start_scheduler()

@app.get("/")
def read_root():
    return {"status": "SaaS Sistemi Aktif", "mode": "Localhost/Ucretsiz"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
