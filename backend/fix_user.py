from sqlmodel import Session, select
from app.models.all_models import User, Plan, Role
from app.database import engine

def check_and_create_user(email, password):
    with Session(engine) as session:
        user = session.exec(select(User).where(User.email == email)).first()
        if user:
            print(f"User EXISTS: {user.email}, ID: {user.id}")
            user.hashed_password = password
            session.add(user)
            session.commit()
            print(f"Password UPDATED for {user.email} to {password}")
        else:
            print(f"User NOT FOUND: {email}. Creating now...")
            # Create Default Plan if missing
            default_plan = session.exec(select(Plan).where(Plan.name == "Basic")).first()
            if not default_plan:
                default_plan = Plan(name="Basic", max_groups=5, max_daily_sends=50, min_delay=30)
                session.add(default_plan)
                session.commit()
                session.refresh(default_plan)
            
            new_user = User(email=email, hashed_password=password, role=Role.USER, plan_id=default_plan.id, full_name="Auto Created")
            session.add(new_user)
            session.commit()
            print(f"User CREATED: {email} with password: {password}")

if __name__ == "__main__":
    # Using a standard password for the fix
    check_and_create_user("arafat2003141@gmail.com", "123456")
