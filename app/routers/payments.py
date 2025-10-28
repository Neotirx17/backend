from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from ..db import get_session
from ..models import Payment, Loan
from ..deps import require_roles
from ..utils import format_pt_date, parse_pt_date

router = APIRouter()

@router.get("")
def list_payments(loan_id: int | None = None, session: Session = Depends(get_session), user = Depends(require_roles("admin", "tecnico", "agente"))):
    query = select(Payment)
    if loan_id:
        query = query.where(Payment.loan_id == loan_id)
    payments = session.exec(query).all()
    return [
        {
            "id": p.id,
            "loanId": p.loan_id,
            "date": format_pt_date(p.date),
            "amount": p.amount,
        }
        for p in payments
    ]

@router.post("")
def create_payment(payload: dict, session: Session = Depends(get_session), user = Depends(require_roles("admin", "tecnico", "agente"))):
    loan_id = payload.get("loanId")
    if not loan_id or not session.get(Loan, loan_id):
        raise HTTPException(status_code=404, detail="Empréstimo não encontrado")
    p = Payment(
        loan_id=loan_id,
        date=parse_pt_date(payload.get("date")),
        amount=payload.get("amount"),
    )
    session.add(p)
    session.commit()
    session.refresh(p)
    return {"id": p.id, "loanId": p.loan_id, "date": format_pt_date(p.date), "amount": p.amount}

@router.delete("/{payment_id}")
def delete_payment(payment_id: int, session: Session = Depends(get_session), user = Depends(require_roles("admin", "tecnico"))):
    p = session.get(Payment, payment_id)
    if not p:
        raise HTTPException(status_code=404, detail="Pagamento não encontrado")
    session.delete(p)
    session.commit()
    return {"ok": True}
