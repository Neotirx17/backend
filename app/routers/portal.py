from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from ..db import get_session
from ..models import Member, Loan, Payment, Fine, ProfitShare
from ..deps import require_roles, get_current_user
from ..utils import format_pt_date

router = APIRouter()

@router.get("/me")
def my_portal(session: Session = Depends(get_session), current = Depends(get_current_user), user = Depends(require_roles("cliente"))):
    if not current.member_id:
        return {"member": None, "loans": [], "payments": [], "fines": [], "profitSharing": []}
    member = session.get(Member, current.member_id)
    loans = session.exec(select(Loan).where(Loan.member_id == current.member_id)).all()
    payments = session.exec(select(Payment).where(Payment.loan_id.in_([l.id for l in loans]))).all()
    fines = session.exec(select(Fine).where(Fine.member_id == current.member_id)).all()
    shares = session.exec(select(ProfitShare).where(ProfitShare.member_id == current.member_id)).all()
    return {
        "member": {
            "id": member.id,
            "name": member.name,
            "memberNumber": member.member_number,
            "contact": member.contact,
            "status": member.status,
        } if member else None,
        "loans": [
            {
                "id": l.id,
                "amount": l.amount,
                "date": format_pt_date(l.date),
                "dueDate": format_pt_date(l.due_date),
                "status": l.status,
            } for l in loans
        ],
        "payments": [
            {
                "id": p.id,
                "loanId": p.loan_id,
                "date": format_pt_date(p.date),
                "amount": p.amount,
            } for p in payments
        ],
        "fines": [
            {
                "id": f.id,
                "reason": f.reason,
                "amount": f.amount,
            } for f in fines
        ],
        "profitSharing": [
            {
                "id": ps.id,
                "amount": ps.amount,
            } for ps in shares
        ],
    }
