from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from models.user import User
from dependencies import get_current_admin_user, get_db

router = APIRouter(
    prefix="/admin",
    tags=["admin-panel"]
)


@router.patch("/promote/{user_id}")
def promote_user(
        user_id: int,
        db: Session = Depends(get_db),
        current_admin: User = Depends(get_current_admin_user)
):

    user_to_promote = db.query(User).filter(User.id == user_id).first()

    if not user_to_promote:
        raise HTTPException(status_code=404, detail="User not found")

    user_to_promote.is_admin = True
    db.commit()
    db.refresh(user_to_promote)

    return {"status": "success", "message": f"User {user_to_promote.username} now is admin"}