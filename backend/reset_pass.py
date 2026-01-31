from sqlmodel import Session, select
from app.models.all_models import User
from app.database import engine

def reset_password(email, new_password):
    with Session(engine) as session:
        user = session.exec(select(User).where(User.email == email)).first()
        if user:
            user.hashed_password = new_password
            session.add(user)
            session.commit()
            print(f"Password RESET for: {email} to {new_password}")
        else:
            print(f"User NOT FOUND: {email}")

if __name__ == "__main__":
    reset_password("arafat2003141@gmail.com", "123456")
