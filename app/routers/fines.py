from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from ..db import get_session
from ..models import Fine, Member
from ..deps import require_roles

router = APIRouter()

@router.get("")
def list_fines(session: Session = Depends(get_session), user = Depends(require_roles("admin", "tecnico", "agente"))):
    fines = session.exec(select(Fine)).all()
    member_map = {m.id: m.name for m in session.exec(select(Member)).all()}
    return [
        {
            "id": f.id,
            "member": member_map.get(f.member_id),
            "memberId": f.member_id,
            "reason": f.reason,
            "amount": f.amount,
        }
        for f in fines
    ]

@router.post("")
def create_fine(payload: dict, session: Session = Depends(get_session), user = Depends(require_roles("admin", "tecnico"))):
    member_id = payload.get("memberId")
    if not member_id or not session.get(Member, member_id):
        raise HTTPException(status_code=404, detail="Membro não encontrado")
    f = Fine(member_id=member_id, reason=payload.get("reason"), amount=payload.get("amount"))
    session.add(f)
    session.commit()
    session.refresh(f)
    return {"id": f.id, "memberId": f.member_id, "reason": f.reason, "amount": f.amount}

@router.delete("/{fine_id}")
def delete_fine(fine_id: int, session: Session = Depends(get_session), user = Depends(require_roles("admin", "tecnico"))):
    f = session.get(Fine, fine_id)
    if not f:
        raise HTTPException(status_code=404, detail="Multa não encontrada")
    session.delete(f)
    session.commit()
    return {"ok": True}
