from sqlmodel import Session, select, create_engine
from app.models.all_models import User, Plan, Role
from app.database import engine, create_db_and_tables # Import create_db_and_tables
import sys

# Re-create engine if import fails or just use the connection string directly
sqlite_url = "sqlite:///database.db"
# engine = create_engine(sqlite_url) # We are importing engine, so no need to redefine unless we want to override

def seed_data():
    create_db_and_tables() # Create tables first
    with Session(engine) as session:
        # 1. Create Plans
        plans = [
            {"name": "Free", "max_groups": 2, "max_daily_sends": 20, "min_delay": 60},
            {"name": "Pro", "max_groups": 20, "max_daily_sends": 1000, "min_delay": 10},
            {"name": "Enterprise", "max_groups": 100, "max_daily_sends": 10000, "min_delay": 5},
        ]
        
        for p_data in plans:
            existing_plan = session.exec(select(Plan).where(Plan.name == p_data["name"])).first()
            if not existing_plan:
                plan = Plan(**p_data)
                session.add(plan)
                print(f"Plan created: {p_data['name']}")
            else:
                print(f"Plan already exists: {p_data['name']}")
        
        session.commit()

        # 2. Create Admin User
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        admin_email = "Arafatimamogluu@gmail.com"
        admin_password_raw = "Arafat141"
        admin_password_hash = pwd_context.hash(admin_password_raw)
        admin_name = "Arafat Imamoglu"
        
        existing_admin = session.exec(select(User).where(User.email == admin_email)).first()
        
        # Get Enterprise plan for admin
        admin_plan = session.exec(select(Plan).where(Plan.name == "Enterprise")).first()
        
        if not existing_admin:
            admin_user = User(
                email=admin_email,
                hashed_password=admin_password_hash, 
                full_name=admin_name,
                role=Role.ADMIN,
                plan_id=admin_plan.id if admin_plan else None,
                is_verified=True # Admin is pre-verified
            )
            session.add(admin_user)
            session.commit()
            print(f"Admin user created: {admin_email}")
        else:
            print(f"Admin user already exists: {admin_email}")
            # Update to admin if somehow not
            existing_admin.role = Role.ADMIN
            existing_admin.hashed_password = admin_password_hash
            existing_admin.plan_id = admin_plan.id if admin_plan else None
            existing_admin.is_verified = True
            session.add(existing_admin)
            session.commit()
            print("Admin user updated.")

if __name__ == "__main__":
    seed_data()
