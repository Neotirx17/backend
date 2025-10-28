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

    # Evolução mensal: soma por mês (Jan-Dez) de empréstimos e pagamentos (ano corrente)
    months_keys = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    loans_monthly = {k: 0.0 for k in months_keys}
    pays_monthly = {k: 0.0 for k in months_keys}
    current_year = today.year
    for l in loans:
        if l.date and l.date.year == current_year:
            key = l.date.strftime("%b")
            if key in loans_monthly:
                loans_monthly[key] += float(l.amount or 0)
    for p in payments:
        if p.date and p.date.year == current_year:
            key = p.date.strftime("%b")
            if key in pays_monthly:
                pays_monthly[key] += float(p.amount or 0)
    monthly_evolution = [
        {"month": m, "loans": loans_monthly[m], "payments": pays_monthly[m]}
        for m in months_keys
    ]

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
