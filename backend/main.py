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

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

# ... (Previous code)

# Serve Frontend (Must be after API routes)
# Check if dist folder exists (Production)
frontend_dist = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend", "dist")

if os.path.exists(frontend_dist):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")
    
    @app.get("/{full_path:path}")
    async def serve_react(full_path: str):
        # Allow API calls to pass through
        if full_path.startswith("api/"):
             return {"status": "404", "message": "API endpoint not found"}
             
        # Serve index.html for all other routes (SPA)
        file_path = os.path.join(frontend_dist, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        
        return FileResponse(os.path.join(frontend_dist, "index.html"))
else:
    @app.get("/")
    def read_root():
        return {"status": "Backend Running (Frontend NOT found in Docker)", "dist_path": frontend_dist}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
