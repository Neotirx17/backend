from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from ..db import get_session
from ..models import Member, Loan
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

@router.delete("/{member_id}")
def delete_member(member_id: int, session: Session = Depends(get_session), user = Depends(require_roles("admin", "tecnico"))):
    m = session.get(Member, member_id)
    if not m:
        return {"ok": False, "detail": "Membro não encontrado"}
    # Impedir exclusão se houver empréstimos vinculados
    has_loans = session.exec(select(Loan).where(Loan.member_id == member_id).limit(1)).first()
    if has_loans:
        return {"ok": False, "detail": "Membro possui empréstimos associados"}
    session.delete(m)
    session.commit()
    return {"ok": True}
