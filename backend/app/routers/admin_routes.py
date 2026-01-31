from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, func
from typing import List, Optional
from pydantic import BaseModel
from app.database import get_session
from app.models.all_models import User, Plan, Task, Group, Role
from app.dependencies import get_current_user

router = APIRouter()

def get_current_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != Role.ADMIN:
        raise HTTPException(status_code=403, detail="Admin yetkisi gerekiyor")
    return current_user

@router.get("/stats")
def get_stats(session: Session = Depends(get_session), admin: User = Depends(get_current_admin)):
    total_users = session.exec(select(func.count(User.id))).one()
    active_users = session.exec(select(func.count(User.id)).where(User.plan_id != None)).one() # Simplification
    # today_messages count logic could be complex, putting 0 for now or getting from logs
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "today_messages": 0,
        "active_tasks": 0
    }

@router.get("/users")
def get_users(session: Session = Depends(get_session), admin: User = Depends(get_current_admin)):
    users = session.exec(select(User)).all()
    # Serialize manually or Use Pydantic response models. 
    # Frontend expects: full_name, email, subscription_plan, is_active
    
    user_list = []
    for u in users:
        plan_name = "Free"
        if u.plan_id:
             plan = session.get(Plan, u.plan_id)
             if plan: plan_name = plan.name

        user_list.append({
            "full_name": getattr(u, "full_name", ""),
            "email": u.email,
            "subscription_plan": plan_name.lower(), # frontend uses lowercase for select values
            "is_active": True # User model might not have is_active, assuming True or adding column later
        })
    
    return {"users": user_list}

@router.put("/users/{email}/plan")
def update_user_plan(email: str, plan: str, session: Session = Depends(get_session), admin: User = Depends(get_current_admin)):
    user = session.exec(select(User).where(User.email == email)).first()
    if not user:
         raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")
    
    # plan string comes as 'pro', 'basic'. Map to DB Plan
    db_plan = session.exec(select(Plan).where(func.lower(Plan.name) == plan.lower())).first()
    if db_plan:
        user.plan_id = db_plan.id
        session.add(user)
        session.commit()
    
    return {"message": "Plan güncellendi"}

@router.put("/users/{email}/status")
def update_user_status(email: str, is_active: bool, session: Session = Depends(get_session), admin: User = Depends(get_current_admin)):
    # If User model has is_active field
    # user = session.exec(select(User).where(User.email == email)).first()
    # user.is_active = is_active
    # session.commit()
    return {"message": "Durum güncellendi (Simülasyon)"}


@router.get("/tasks")
def get_tasks(session: Session = Depends(get_session), admin: User = Depends(get_current_admin)):
    # Return dummy or real tasks
    return {"tasks": []}

@router.get("/plans")
def get_plans(session: Session = Depends(get_session), admin: User = Depends(get_current_admin)):
    plans = session.exec(select(Plan)).all()
    return {"plans": [
        {
            "plan_name": p.name,
            "max_groups": p.max_groups,
            "max_daily_sends": p.max_daily_sends,
            "max_scheduled_times": 24, # default
            "min_delay_seconds": p.min_delay,
            "price_monthly": 0
        }
        for p in plans
    ]}

@router.get("/settings")
def get_settings(session: Session = Depends(get_session), admin: User = Depends(get_current_admin)):
    return {"settings": {}}

@router.get("/logs")
def get_logs(session: Session = Depends(get_session), admin: User = Depends(get_current_admin)):
    return {"failed_logs": []}
