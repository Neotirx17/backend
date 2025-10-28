from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from ..db import get_session
from ..models import User, Member
from ..deps import require_roles
from ..security import get_password_hash

router = APIRouter()

@router.get("")
def list_users(session: Session = Depends(get_session), user = Depends(require_roles("admin"))):
    users = session.exec(select(User)).all()
    return [
        {
            "id": u.id,
            "username": u.username,
            "role": u.role,
            "name": u.name,
            "memberId": u.member_id,
        }
        for u in users
    ]

@router.get("/{user_id}")
def get_user(user_id: int, session: Session = Depends(get_session), user = Depends(require_roles("admin"))):
    u = session.get(User, user_id)
    if not u:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return {"id": u.id, "username": u.username, "role": u.role, "name": u.name, "memberId": u.member_id}

@router.post("")
def create_user(payload: dict, session: Session = Depends(get_session), user = Depends(require_roles("admin"))):
    username = payload.get("username")
    password = payload.get("password")
    role = payload.get("role")
    name = payload.get("name")
    member_id = payload.get("memberId")
    if not username or not password or not role:
        raise HTTPException(status_code=400, detail="username, password e role são obrigatórios")
    exists = session.exec(select(User).where(User.username == username)).first()
    if exists:
        raise HTTPException(status_code=409, detail="Usuário já existe")
    if member_id and not session.get(Member, member_id):
        raise HTTPException(status_code=404, detail="Membro não encontrado")
    u = User(username=username, password_hash=get_password_hash(password), role=role, name=name or username, member_id=member_id)
    session.add(u)
    session.commit()
    session.refresh(u)
    return {"id": u.id, "username": u.username, "role": u.role, "name": u.name, "memberId": u.member_id}

@router.put("/{user_id}")
def update_user(user_id: int, payload: dict, session: Session = Depends(get_session), user = Depends(require_roles("admin"))):
    u = session.get(User, user_id)
    if not u:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    if "username" in payload:
        new_username = payload.get("username")
        if new_username and new_username != u.username:
            exists = session.exec(select(User).where(User.username == new_username)).first()
            if exists:
                raise HTTPException(status_code=409, detail="Username em uso")
            u.username = new_username
    if "password" in payload and payload.get("password"):
        u.password_hash = get_password_hash(payload.get("password"))
    if "role" in payload and payload.get("role"):
        u.role = payload.get("role")
    if "name" in payload:
        u.name = payload.get("name") or u.name
    if "memberId" in payload:
        member_id = payload.get("memberId")
        if member_id and not session.get(Member, member_id):
            raise HTTPException(status_code=404, detail="Membro não encontrado")
        u.member_id = member_id
    session.add(u)
    session.commit()
    session.refresh(u)
    return {"id": u.id, "username": u.username, "role": u.role, "name": u.name, "memberId": u.member_id}

@router.delete("/{user_id}")
def delete_user(user_id: int, session: Session = Depends(get_session), user = Depends(require_roles("admin"))):
    u = session.get(User, user_id)
    if not u:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    session.delete(u)
    session.commit()
    return {"ok": True}
