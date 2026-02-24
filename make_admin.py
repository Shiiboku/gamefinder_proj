from db import database
from models.user import User
import os
from dotenv import load_dotenv
load_dotenv()

USERNAME_TO_PROMOTE = os.getenv('USERNAME_TO_PROMOTE')

def promote_to_admin():
    if not USERNAME_TO_PROMOTE:
        print("Please set USERNAME_TO_PROMOTE environment variable")
        return
    try:
        with database.get_session() as db:
            user = db.query(User).filter(User.username == USERNAME_TO_PROMOTE).first()
            if user:
                if user.is_admin:
                    print(f"user {USERNAME_TO_PROMOTE} already admin.")
                else:
                    user.is_admin = True
                    db.commit()
                    print(f"user {USERNAME_TO_PROMOTE} promoted to admin.")
            else:
                print(f"user {USERNAME_TO_PROMOTE} not found.")
    except Exception as e:
        print(f"An error occurred while working with the database: {e}")

if __name__ == "__main__":
    promote_to_admin()