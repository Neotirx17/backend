from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from ..db import get_session
from ..models import Loan, Member, Payment
from ..deps import require_roles
from ..utils import format_pt_date, parse_pt_date
from datetime import date as _date

router = APIRouter()

@router.get("")
def list_loans(session: Session = Depends(get_session), user = Depends(require_roles("admin", "tecnico", "agente"))):
    loans = session.exec(select(Loan)).all()
    member_map = {m.id: m.name for m in session.exec(select(Member)).all()}
    payments = session.exec(select(Payment)).all()
    paid_map: dict[int, float] = {}
    for p in payments:
        paid_map[p.loan_id] = paid_map.get(p.loan_id, 0.0) + float(p.amount or 0)
    today = _date.today()
    return [
        {
            "id": l.id,
            "member": member_map.get(l.member_id),
            "memberId": l.member_id,
            "amount": l.amount,
            "date": format_pt_date(l.date),
            "dueDate": format_pt_date(l.due_date),
            "totalPaid": paid_map.get(l.id, 0.0),
            "remaining": max(float(l.amount or 0) - paid_map.get(l.id, 0.0), 0.0),
            "status": (
                "Liquidado" if max(float(l.amount or 0) - paid_map.get(l.id, 0.0), 0.0) <= 0.0 else (
                    "Em atraso" if (l.due_date and l.due_date < today) else (l.status or "Em dia")
                )
            ),
        }
        for l in loans
    ]

@router.post("")
def create_loan(payload: dict, session: Session = Depends(get_session), user = Depends(require_roles("admin", "tecnico"))):
    member_id = payload.get("memberId")
    if not member_id:
        raise HTTPException(status_code=400, detail="memberId é obrigatório")
    if not session.get(Member, member_id):
        raise HTTPException(status_code=404, detail="Membro não encontrado")
    l = Loan(
        member_id=member_id,
        amount=payload.get("amount"),
        date=parse_pt_date(payload.get("date")),
        due_date=parse_pt_date(payload.get("dueDate")),
        status=payload.get("status", "Em dia"),
    )
    session.add(l)
    session.commit()
    session.refresh(l)
    m = session.get(Member, l.member_id)
    return {
        "id": l.id,
        "member": m.name if m else None,
        "memberId": l.member_id,
        "amount": l.amount,
        "date": format_pt_date(l.date),
        "dueDate": format_pt_date(l.due_date),
        "status": l.status,
    }
