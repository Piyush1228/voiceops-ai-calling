from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.modules.calls import service
from app.modules.calls.schemas import CallCreate, CallOut
from app.modules.users.models import User

router = APIRouter(prefix="/calls", tags=["Calls"])


@router.post("", response_model=CallOut, status_code=status.HTTP_201_CREATED)
def create_call(
    payload: CallCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.create_call(db, current_user, payload)


@router.get("", response_model=list[CallOut])
def list_calls(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.list_calls(db, current_user, skip, limit)


@router.get("/{call_id}", response_model=CallOut)
def get_call(
    call_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.get_call(db, current_user, call_id)