from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List, Optional
from pydantic import BaseModel
from ..database import get_session
from ..models.all_models import User, Group, Campaign

router = APIRouter()

# --- Modeller ---
class GroupCreate(BaseModel):
    user_id: int
    name: str
    target_identifier: str

class CampaignCreate(BaseModel):
    user_id: int
    name: str
    message_content: str
    schedule_times: str # "08:00,12:00"
    target_group_ids: str # "1,2,3"
    delay_seconds: int

# --- Gruplar ---
@router.post("/groups")
def add_group(group_data: GroupCreate, session: Session = Depends(get_session)):
    new_group = Group(
        name=group_data.name,
        target_identifier=group_data.target_identifier,
        user_id=group_data.user_id,
        is_active=True
    )
    session.add(new_group)
    session.commit()
    return {"message": "Grup eklendi", "group": new_group}

@router.get("/groups/{user_id}")
def get_user_groups(user_id: int, session: Session = Depends(get_session)):
    groups = session.exec(select(Group).where(Group.user_id == user_id)).all()
    return groups

@router.delete("/groups/{group_id}")
def delete_group(group_id: int, session: Session = Depends(get_session)):
    group = session.get(Group, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Grup bulunamadı")
    session.delete(group)
    session.commit()
    return {"message": "Grup silindi"}

# --- Kampanyalar (Planlar) ---
@router.post("/campaigns")
def save_campaign(camp_data: CampaignCreate, session: Session = Depends(get_session)):
    # Varsa güncelle, yoksa oluştur mantığı yerine şimdilik direkt ekleyelim
    new_camp = Campaign(
        user_id=camp_data.user_id,
        name=camp_data.name,
        message_content=camp_data.message_content,
        schedule_times=camp_data.schedule_times,
        target_group_ids=camp_data.target_group_ids,
        delay_seconds=camp_data.delay_seconds,
        is_active=True
    )
    session.add(new_camp)
    session.commit()
    return {"message": "Kampanya kaydedildi", "id": new_camp.id}

@router.get("/campaigns/{user_id}")
def get_campaigns(user_id: int, session: Session = Depends(get_session)):
    camps = session.exec(select(Campaign).where(Campaign.user_id == user_id)).all()
    return camps
