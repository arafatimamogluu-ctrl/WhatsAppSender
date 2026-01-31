from fastapi import Depends, HTTPException, Header, status
from sqlmodel import Session
from jose import jwt, JWTError
from app.database import get_session
from app.models.all_models import User

# TODO: Move to config
SECRET_KEY = "SUPER_SECRET_KEY_CHANGE_THIS"
ALGORITHM = "HS256"

def get_current_user(authorization: str = Header(None), session: Session = Depends(get_session)):
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token bulunamadı")
    
    try:
        parts = authorization.split()
        if len(parts) != 2:
             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Geçersiz token formatı")
             
        scheme, token = parts
        if scheme.lower() != 'bearer':
             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Geçersiz token şeması")
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token geçersiz")
        
        user = session.get(User, int(user_id))
        if not user:
             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Kullanıcı bulunamadı")
             
        return user
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token hatalı or expired")
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token formatı hatalı")
