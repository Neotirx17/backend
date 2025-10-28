from datetime import datetime
from sqlmodel import Session, select
from .db import engine
from .models import User, Member, Loan, Payment, Fine, ProfitShare
from .security import get_password_hash

def parse_pt_date(d: str):
    # Expecting DD/MM/YYYY
    return datetime.strptime(d, "%d/%m/%Y").date()

def seed_db():
    with Session(engine) as session:
        # Seed only if no users
        if session.exec(select(User)).first():
            return
        # Users
        u_admin = User(username="admin", password_hash=get_password_hash("admin123"), role="admin", name="Administrador")
        u_tecnico = User(username="tecnico", password_hash=get_password_hash("tecnico123"), role="tecnico", name="Técnico Adm.")
        u_agente = User(username="agente", password_hash=get_password_hash("agente123"), role="agente", name="Agente de Campo")
        session.add_all([u_admin, u_tecnico, u_agente])
        # Members
        m_joaquim = Member(name="Joaquim", member_number="102", contact="84 123 4567", status="Ativo")
        m_maria = Member(name="Maria", member_number="214", contact="82 567 8901", status="Ativo")
        m_luis = Member(name="Luis", member_number="156", contact="86 345 6789", status="Ativo")
        m_ines = Member(name="Inês", member_number="187", contact="83 654 3210", status="Ativo")
        session.add_all([m_joaquim, m_maria, m_luis, m_ines])
        session.flush()
        u_cliente = User(username="cliente", password_hash=get_password_hash("cliente123"), role="cliente", name="Cliente", member_id=m_maria.id)
        session.add(u_cliente)
        # Loans
        l1 = Loan(member_id=m_joaquim.id, amount=1000.0, date=parse_pt_date("20/02/2025"), due_date=parse_pt_date("20/05/2025"), status="Em dia")
        l2 = Loan(member_id=m_maria.id, amount=500.0, date=parse_pt_date("10/01/2025"), due_date=parse_pt_date("10/04/2025"), status="Em atraso")
        l3 = Loan(member_id=m_luis.id, amount=800.0, date=parse_pt_date("05/12/2024"), due_date=parse_pt_date("05/03/2025"), status="Em dia")
        session.add_all([l1, l2, l3])
        session.flush()
        # Payments
        p1 = Payment(loan_id=l1.id, date=parse_pt_date("25/02/2025"), amount=300.0)
        p2 = Payment(loan_id=l1.id, date=parse_pt_date("20/03/2025"), amount=300.0)
        p3 = Payment(loan_id=l2.id, date=parse_pt_date("15/01/2025"), amount=100.0)
        session.add_all([p1, p2, p3])
        # Fines
        f1 = Fine(member_id=m_joaquim.id, reason="Falta à reunião", amount=15.0)
        f2 = Fine(member_id=m_maria.id, reason="Atraso", amount=5.0)
        f3 = Fine(member_id=m_luis.id, reason="Falta à reunião", amount=10.0)
        session.add_all([f1, f2, f3])
        # Profit Shares
        ps1 = ProfitShare(member_id=m_joaquim.id, amount=200.0)
        ps2 = ProfitShare(member_id=m_maria.id, amount=180.0)
        ps3 = ProfitShare(member_id=m_luis.id, amount=220.0)
        session.add_all([ps1, ps2, ps3])
        session.commit()
