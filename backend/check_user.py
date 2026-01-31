from sqlmodel import Session, select, create_engine
from app.models.all_models import User
# Assuming sqlite url is in database.py or we can guess it
# Let's import engine from app.database if possible, or recreate it
from app.database import engine

def check_user(email):
    with Session(engine) as session:
        user = session.exec(select(User).where(User.email == email)).first()
        if user:
            print(f"User found: {user.email}, ID: {user.id}")
        else:
            print(f"User NOT found: {email}")
            
if __name__ == "__main__":
    check_user("Arafatimamogluu@gmail.com")
