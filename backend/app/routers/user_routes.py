from fastapi import APIRouter, Depends
from sqlmodel import Session, select, func
from typing import List, Optional
from pydantic import BaseModel
from app.database import get_session
from app.models.all_models import User, Group, Campaign, Task
from app.dependencies import get_current_user

router = APIRouter()

# --- Modeller ---
class GroupCreate(BaseModel):
    name: str
    group_id: str
    is_active: bool = True

class MessageData(BaseModel):
    message_type: str
    content: Optional[str] = None
    file_path: Optional[str] = None

class ScheduleData(BaseModel):
    send_times: List[str]
    delay_seconds: int

class DirectMessageData(BaseModel):
    phone: str
    message: str

# --- Gruplar ---
@router.get("/groups")
def get_my_groups(current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    # Return format matching Frontend: { groups: [...] }
    # Also ensuring 'group_id' field is present as frontend expects it (it seems frontend sends 'group_id' as target_identifier?)
    # Frontend: name, group_id, is_active
    # DB: name, target_identifier, is_active
    
    groups = session.exec(select(Group).where(Group.user_id == current_user.id)).all()
    
    # Transform to match frontend expectation if needed, or update frontend to use target_identifier
    # Dashboard.js uses group.group_id as key.
    # So we should map target_identifier -> group_id in response
    return {
        "groups": [
            {
                "name": g.name, 
                "group_id": g.target_identifier, 
                "is_active": g.is_active, 
                "participants": 0 # Placeholder
            } 
            for g in groups
        ]
    }

@router.post("/groups")
def add_group(group_data: GroupCreate, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    # Limit Kontrolü
    if current_user.plan:
        current_count = len(current_user.groups)
        if current_count >= current_user.plan.max_groups:
             return {"message": f"Paket limitine ulaştınız ({current_user.plan.max_groups} grup)."}

    # Check duplicate
    existing = session.exec(select(Group).where(Group.target_identifier == group_data.group_id, Group.user_id == current_user.id)).first()
    if existing:
        return {"message": "Grup zaten ekli"}

    new_group = Group(
        name=group_data.name,
        target_identifier=group_data.group_id,
        user_id=current_user.id,
        is_active=group_data.is_active
    )
    session.add(new_group)
    session.commit()
    return {"message": "Grup eklendi"}

@router.post("/groups/sync")
def sync_groups(current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    from app.services.whatsapp_service import whatsapp_service
    
    if not whatsapp_service.is_logged_in():
        return {"message": "WhatsApp bağlı değil. Önce bağlanın.", "groups": []}

    # WhatsApp'tan çek
    whatsapp_chats = whatsapp_service.get_chats() # Returns list of dicts {name, id, type, ...}
    
    added_count = 0
    updated_count = 0
    
    for chat in whatsapp_chats:
        # Check limit
        if current_user.plan and len(current_user.groups) >= current_user.plan.max_groups:
             break # Stop if limit reached
             
        # Check if exists
        target_id = chat["id"] # Use name as ID for now as per service logic
        
        existing = session.exec(select(Group).where(
            Group.target_identifier == target_id, 
            Group.user_id == current_user.id
        )).first()
        
        if existing:
            # Update info if needed (e.g. participant count if we had it)
            updated_count += 1
        else:
            new_group = Group(
                name=chat["name"],
                target_identifier=target_id,
                user_id=current_user.id,
                is_active=True
            )
            session.add(new_group)
            added_count += 1
            
    session.commit()
    
    # Return updated list
    groups = session.exec(select(Group).where(Group.user_id == current_user.id)).all()
    return {
        "message": f"Senkronizasyon tamamlandı. {added_count} yeni, {updated_count} güncellendi.",
        "groups": [
            {
                "name": g.name, 
                "group_id": g.target_identifier, 
                "is_active": g.is_active, 
                "participants": 0
            } 
            for g in groups
        ]
    }

@router.delete("/groups/{group_id}")
def delete_group(group_id: str, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    # Frontend sends group_id (target_identifier) string in path? Or database ID?
    # Dashboard.js: api.delete(/user/groups/${groupId}) where groupId is group.group_id (target_identifier)
    
    # Try finding by target_identifier (string)
    group = session.exec(
        select(Group).where(Group.target_identifier == group_id, Group.user_id == current_user.id)
    ).first()
    
    # If not found, try finding by numeric ID (if frontend sent int)
    if not group and group_id.isdigit():
         group = session.get(Group, int(group_id))
         if group and group.user_id != current_user.id:
             group = None

    if group:
        session.delete(group)
        session.commit()
    return {"message": "Grup silindi"}

# --- Mesaj ---
@router.get("/message")
def get_message(current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    # Get active campaign or last created campaign
    camp = session.exec(select(Campaign).where(Campaign.user_id == current_user.id)).first()
    if camp:
        return {"message": {"message_type": "text", "content": camp.message_content}}
    return {"message": None}

@router.post("/message")
def save_message(msg: MessageData, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    # Save as a Campaign (simplified)
    # Placeholder implementation
    return {"message": "Mesaj kaydedildi"}

# --- Zamanlama ---
@router.get("/schedule")
def get_schedule(current_user: User = Depends(get_current_user)):
    return {"schedule": {"send_times": ["09:00"], "delay_seconds": 10}}

@router.post("/schedule")
def save_schedule(data: ScheduleData, current_user: User = Depends(get_current_user)):
    return {"message": "Zamanlama kaydedildi"}

# --- Loglar ---
@router.get("/logs")
def get_logs(current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    tasks = session.exec(select(Task).where(Task.user_id == current_user.id)).all()
    logs = [
        {
            "group_name": t.target_group_name,
            "status": "completed" if t.status == "tamamlandi" else "failed",
            "message_type": "text",
            "scheduled_time": t.created_at.strftime("%H:%M")
        }
        for t in tasks
    ]
    return {"logs": logs}

# --- Gönderim İşlemleri ---
@router.post("/send-now")
def send_now(current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    from app.services.whatsapp_service import whatsapp_service
    from datetime import datetime, date

    # 1. Limit Kontrolü
    if current_user.plan:
        today = date.today()
        todays_tasks = session.exec(select(Task).where(
            Task.user_id == current_user.id, 
            func.date(Task.created_at) == today
        )).all()
        
        if len(todays_tasks) >= current_user.plan.max_daily_sends:
             return {"message": f"Günlük gönderim limitine ulaştınız ({current_user.plan.max_daily_sends} mesaj)."}

    # 2. Son Kampanyayı Bul
    camp = session.exec(select(Campaign).where(Campaign.user_id == current_user.id).order_by(Campaign.id.desc())).first()
    if not camp or not camp.message_content:
        return {"message": "Gönderilecek mesaj bulunamadı. Önce mesaj kaydedin."}

    # 3. İlgili Grupları Bul
    # Eğer specific bir seçim varsa (target_group_ids), sadece onlara gönder. 
    # Yoksa aktif olanlara mı? CampaignBuilder 'all' gönderiyor özel durum için.
    
    target_ids = []
    if camp.target_group_ids and camp.target_group_ids != "all":
        target_ids = camp.target_group_ids.split(",")
    
    query = select(Group).where(Group.user_id == current_user.id, Group.is_active == True)
    
    if target_ids:
        # Filter by target_identifier since that's what we stored/passed? 
        # Wait, Frontend GroupManager passed 'group_id' which is 'target_identifier'.
        query = query.where(Group.target_identifier.in_(target_ids))
        
    groups = session.exec(query).all()
    
    if not groups:
        return {"message": "Hedef grup bulunamadı."}

    # 4. Gönderimi Başlat
    success_count = 0
    fail_count = 0
    
    if not whatsapp_service.is_logged_in():
         return {"message": "WhatsApp bağlı değil. Önce QR kodu taratın."}

    # Delay handling?
    import time
    delay = camp.delay_seconds if camp.delay_seconds else 10

    for i, group in enumerate(groups):
        if i > 0 and delay > 0:
            time.sleep(delay)

        task = Task(
            user_id=current_user.id,
            target_group_name=group.name,
            message_content=camp.message_content,
            status="calisiyor",
            created_at=datetime.now()
        )
        session.add(task)
        session.commit()
        session.refresh(task)

        try:
            result, msg = whatsapp_service.send_message(group.target_identifier, camp.message_content)
            
            if result:
                task.status = "tamamlandi"
                task.result_log = "Başarılı"
                success_count += 1
            else:
                task.status = "hatali"
                task.result_log = msg
                fail_count += 1
                
        except Exception as e:
            task.status = "hatali"
            task.result_log = str(e)
            fail_count += 1
        
        task.executed_at = datetime.now()
        session.add(task)
        session.commit()
    
    return {"message": f"İşlem tamamlandı. Başarılı: {success_count}, Hatalı: {fail_count}"}

@router.post("/send-direct")
def send_direct(data: DirectMessageData, current_user: User = Depends(get_current_user)):
    from app.services.whatsapp_service import whatsapp_service
    
    if not whatsapp_service.is_logged_in():
        return {"message": "WhatsApp bağlı değil."}
        
    success, msg = whatsapp_service.send_direct_message(data.phone, data.message)
    if success:
        return {"message": "Mesaj gönderildi"}
    else:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail=f"Gönderim başarısız: {msg}")
