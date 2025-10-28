from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from ..db import get_session
from ..models import Member
from ..deps import require_roles

router = APIRouter()

@router.get("")
def list_members(session: Session = Depends(get_session), user = Depends(require_roles("admin", "tecnico", "agente"))):
    members = session.exec(select(Member)).all()
    # shape similar ao mock: id, name, memberNumber, contact, status
    return [
        {
            "id": m.id,
            "name": m.name,
            "memberNumber": m.member_number,
            "contact": m.contact,
            "status": m.status,
        }
        for m in members
    ]

@router.post("")
def create_member(payload: dict, session: Session = Depends(get_session), user = Depends(require_roles("admin", "tecnico"))):
    m = Member(
        name=payload.get("name"),
        member_number=payload.get("memberNumber"),
        contact=payload.get("contact"),
        status=payload.get("status", "Ativo"),
    )
    session.add(m)
    session.commit()
    session.refresh(m)
    return {
        "id": m.id,
        "name": m.name,
        "memberNumber": m.member_number,
        "contact": m.contact,
        "status": m.status,
    }
