from datetime import date, datetime

PT_DATE_FMT = "%d/%m/%Y"

def parse_pt_date(d: str) -> date:
    return datetime.strptime(d, PT_DATE_FMT).date()

def format_pt_date(d: date | None) -> str | None:
    if d is None:
        return None
    return d.strftime(PT_DATE_FMT)
