from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from ..db import get_session
from ..models import ProfitShare, Member
from ..deps import require_roles

router = APIRouter()

@router.get("")
def list_profit(session: Session = Depends(get_session), user = Depends(require_roles("admin", "tecnico", "agente"))):
    shares = session.exec(select(ProfitShare)).all()
    member_map = {m.id: m.name for m in session.exec(select(Member)).all()}
    return [
        {
            "id": ps.id,
            "member": member_map.get(ps.member_id),
            "memberId": ps.member_id,
            "amount": ps.amount,
        }
        for ps in shares
    ]

@router.post("")
def create_profit(payload: dict, session: Session = Depends(get_session), user = Depends(require_roles("admin", "tecnico"))):
    member_id = payload.get("memberId")
    if not member_id or not session.get(Member, member_id):
        raise HTTPException(status_code=404, detail="Membro não encontrado")
    ps = ProfitShare(member_id=member_id, amount=payload.get("amount"))
    session.add(ps)
    session.commit()
    session.refresh(ps)
    return {"id": ps.id, "memberId": ps.member_id, "amount": ps.amount}

@router.delete("/{profit_id}")
def delete_profit(profit_id: int, session: Session = Depends(get_session), user = Depends(require_roles("admin", "tecnico"))):
    ps = session.get(ProfitShare, profit_id)
    if not ps:
        raise HTTPException(status_code=404, detail="Partilha não encontrada")
    session.delete(ps)
    session.commit()
    return {"ok": True}
