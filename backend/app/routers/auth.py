from datetime import datetime, timedelta
import random
import string
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import jwt, JWTError
from ..database import get_session
from ..models.all_models import User, Plan, Role

router = APIRouter()

# Config
SECRET_KEY = "SUPER_SECRET_KEY_CHANGE_THIS" # In prod, use env
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 # 1 day

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserRegister(BaseModel):
    email: str
    password: str
    full_name: str | None = None

class UserLogin(BaseModel):
    email: str
    password: str

class VerifyOTP(BaseModel):
    email: str
    otp_code: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: dict

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister, session: Session = Depends(get_session)):
    try:
        existing_user = session.exec(select(User).where(User.email == user_data.email)).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Bu email zaten kayıtlı.")
        
        # Password policy check (basic)
        if len(user_data.password) < 8:
             raise HTTPException(status_code=400, detail="Şifre en az 8 karakter olmalıdır.")

        otp = generate_otp()
        otp_expiry = datetime.utcnow() + timedelta(minutes=5)
        
        hashed_pwd = get_password_hash(user_data.password)
        
        new_user = User(
            email=user_data.email, 
            hashed_password=hashed_pwd, 
            role=Role.USER,
            full_name=user_data.full_name,
            otp_code=otp,
            otp_expiry=otp_expiry,
            is_verified=True # Auto-verify users (User request: No code for login)
        )

        # Assign Default Plan
        default_plan = session.exec(select(Plan).where(Plan.name == "Free")).first()
        if not default_plan:
             # Create default plans if not exist (fail-safe)
             default_plan = Plan(name="Free", max_groups=2, max_daily_sends=20, min_delay=60)
             session.add(default_plan)
             session.commit()
             session.refresh(default_plan)
        
        new_user.plan_id = default_plan.id
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        
        # TODO: Send Email with OTP. For now, we return it for testing/debugging.
        print(f"DEBUG OTP for {user_data.email}: {otp}")
        
        return {
            "message": "Kayıt başarılı. Lütfen email adresinize gönderilen doğrulama kodunu giriniz.",
            "email": new_user.email,
            "debug_otp": otp # REMOVE IN PROD
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_msg = f"Registration Error: {str(e)} \nTraceback: {traceback.format_exc()}"
        print(error_msg)
        raise HTTPException(status_code=500, detail=f"Sunucu Hatası: {str(e)}")


@router.post("/verify-otp")
def verify_user_otp(data: VerifyOTP, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == data.email)).first()
    if not user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")
        
    if user.is_verified:
         # Already verified, just login
         access_token = create_access_token(data={"sub": str(user.id), "role": user.role})
         return {
            "message": "Hesap zaten doğrulanmış",
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                 "id": user.id,
                 "email": user.email,
                 "role": user.role,
                 "full_name": user.full_name
            }
         }
         
    if not user.otp_code or not user.otp_expiry:
        raise HTTPException(status_code=400, detail="Doğrulama kodu bulunamadı. Lütfen yeni kod isteyin.")
        
    if user.otp_code != data.otp_code:
        raise HTTPException(status_code=400, detail="Hatalı doğrulama kodu")
        
    if datetime.utcnow() > user.otp_expiry:
         raise HTTPException(status_code=400, detail="Kodun süresi dolmuş. Tekrar kayıt olun.")
         
    user.is_verified = True
    user.otp_code = None
    session.add(user)
    session.commit()
    
    # Auto login
    access_token = create_access_token(data={"sub": str(user.id), "role": user.role})
    
    return {
        "message": "Hesap doğrulandı",
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
             "id": user.id,
             "email": user.email,
             "role": user.role,
             "full_name": user.full_name
        }
    }

@router.post("/login")
def login(user_data: UserLogin, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == user_data.email)).first()
    
    if not user:
        # Avoid user enumeration
        raise HTTPException(status_code=401, detail="Hatalı email veya şifre")
        
    # Check Lockout
    if user.failed_login_attempts >= 3:
        if user.last_failed_login:
             lockout_end = user.last_failed_login + timedelta(minutes=15)
             if datetime.utcnow() < lockout_end:
                 raise HTTPException(status_code=429, detail="Çok fazla başarısız deneme. 15 dakika bekleyin.")
             else:
                 # Reset if time passed
                 user.failed_login_attempts = 0
                 session.add(user)
                 session.commit()
    
    if not verify_password(user_data.password, user.hashed_password):
        user.failed_login_attempts += 1
        user.last_failed_login = datetime.utcnow()
        session.add(user)
        session.commit()
        remaining = 3 - user.failed_login_attempts
        msg = f"Hatalı şifre."
        if remaining > 0:
            msg += f" Kalan hak: {remaining}"
        else:
            msg += " Hesabınız geçici olarak kilitlendi."
        raise HTTPException(status_code=401, detail=msg)
    
    # Reset failures on success
    if user.failed_login_attempts > 0:
        user.failed_login_attempts = 0
        session.add(user)
        session.commit()
        
    access_token = create_access_token(data={"sub": str(user.id), "role": user.role})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "role": user.role,
            "full_name": user.full_name,
            "subscription_plan": user.plan.name if user.plan else "N/A"
        }
    }
