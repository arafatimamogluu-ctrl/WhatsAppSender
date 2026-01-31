from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from enum import Enum

class Role(str, Enum):
    ADMIN = "admin"
    USER = "user"

class TaskStatus(str, Enum):
    PENDING = "bekliyor"
    RUNNING = "calisiyor"
    COMPLETED = "tamamlandi"
    FAILED = "hatali"

class Plan(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    max_groups: int
    max_daily_sends: int
    min_delay: int = 10
    users: List["User"] = Relationship(back_populates="plan")

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    full_name: Optional[str] = None
    hashed_password: str
    role: Role = Field(default=Role.USER)
    
    plan_id: Optional[int] = Field(default=None, foreign_key="plan.id")
    plan: Optional[Plan] = Relationship(back_populates="users")
    
    groups: List["Group"] = Relationship(back_populates="user")
    campaigns: List["Campaign"] = Relationship(back_populates="user")
    tasks: List["Task"] = Relationship(back_populates="user")

    # Security fields
    otp_code: Optional[str] = None
    otp_expiry: Optional[datetime] = None
    failed_login_attempts: int = Field(default=0)
    last_failed_login: Optional[datetime] = None
    is_verified: bool = Field(default=False)

class Group(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    target_identifier: str # Telefon no veya Grup adı
    is_active: bool = True
    user_id: int = Field(foreign_key="user.id")
    user: User = Relationship(back_populates="groups")

class Campaign(SQLModel, table=True):
    """Kullanıcının kaydettiği gönderim planı"""
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str # Plan Adı
    message_content: str
    media_path: Optional[str] = None
    
    # Seçilen grupların ID'leri (Virgülle ayrılmış string olarak tutacağız basitlik için: "1,2,5")
    # Veya User'ın tüm aktif gruplarına gönderim yapılacaksa basitçe flag tutulabilir.
    target_group_ids: str 
    
    # Gönderim saatleri (Örn: "08:00,12:00,20:00")
    schedule_times: str 
    
    delay_seconds: int = 10
    is_active: bool = True
    
    user_id: int = Field(foreign_key="user.id")
    user: User = Relationship(back_populates="campaigns")

class Task(SQLModel, table=True):
    """Gerçekleşecek her bir gönderim işlemi"""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    user: User = Relationship(back_populates="tasks")
    
    target_group_name: str # O anki hedef
    message_content: str
    media_path: Optional[str] = None
    
    status: TaskStatus = Field(default=TaskStatus.PENDING)
    created_at: datetime = Field(default_factory=datetime.now)
    executed_at: Optional[datetime] = None
    result_log: Optional[str] = None
