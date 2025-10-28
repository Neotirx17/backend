from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from ..db import get_session
from ..models import Loan, Payment
from ..deps import require_roles
from ..utils import format_pt_date
from datetime import date

router = APIRouter()

@router.get("/summary")
def summary(session: Session = Depends(get_session), user = Depends(require_roles("admin", "tecnico", "agente"))):
    loans = session.exec(select(Loan)).all()
    payments = session.exec(select(Payment)).all()

    total_loaned = sum(float(l.amount or 0) for l in loans)
    # Map loan -> total paid
    paid_map: dict[int, float] = {}
    for p in payments:
        paid_map[p.loan_id] = paid_map.get(p.loan_id, 0.0) + float(p.amount or 0)
    total_paid = sum(float(p.amount or 0) for p in payments)
    total_outstanding = sum(max(float(l.amount or 0) - paid_map.get(l.id, 0.0), 0.0) for l in loans)

    # Próximos pagamentos: parcelas com dueDate nos próximos 30 dias (simplificado)
    today = date.today()
    next_30 = date.fromordinal(today.toordinal() + 30)
    upcoming = sum(float(l.amount or 0) for l in loans if l.due_date and today <= l.due_date <= next_30)

    # Evolução mensal (simplificada): soma do valor dos empréstimos por mês do ano corrente
    monthly = {}
    for l in loans:
        if l.date:
            key = l.date.strftime("%b")  # Jan, Fev, ... (em inglês por padrão)
            monthly[key] = monthly.get(key, 0) + float(l.amount or 0)
    monthly_evolution = [{"month": m, "value": v} for m, v in monthly.items()]

    alerts = []
    for l in loans:
        if l.due_date and l.due_date == today:
            alerts.append({"type": "payment", "message": "Pagamento vencido hoje"})
            break

    return {
        "totalLoaned": total_loaned,
        "totalPaid": total_paid,
        "totalOutstanding": total_outstanding,
        "upcomingPayments": upcoming,
        "monthlyEvolution": monthly_evolution,
        "alerts": alerts,
    }
