from calendar import monthrange
from datetime import date, datetime

from ...extensions import db
from ...models import Receivable, ReceivableStatus, Student


def month_start(value):
    return value.replace(day=1)


def add_months(value, months):
    year = value.year + ((value.month - 1 + months) // 12)
    month = ((value.month - 1 + months) % 12) + 1
    return date(year, month, 1)


def due_date_for(reference_month, payment_day):
    last_day = monthrange(reference_month.year, reference_month.month)[1]
    return reference_month.replace(day=min(payment_day, last_day))


def generate_receivables(student: Student, start_month: date, quantity: int):
    created = []
    skipped = 0
    for index in range(quantity):
        reference = add_months(month_start(start_month), index)
        exists = db.session.scalar(
            db.select(Receivable.id).where(
                Receivable.student_id == student.id,
                Receivable.reference_month == reference,
            )
        )
        if exists:
            skipped += 1
            continue

        receivable = Receivable(
            student=student,
            reference_month=reference,
            due_date=due_date_for(reference, student.payment_day),
            amount=student.current_fee(),
            status=ReceivableStatus.OPEN,
        )
        db.session.add(receivable)
        created.append(receivable)
    return created, skipped


def mark_boleto_generated(receivable: Receivable, our_number=None, digitable_line=None):
    receivable.boleto_generated = True
    receivable.boleto_generated_at = datetime.utcnow()
    receivable.boleto_our_number = our_number or receivable.boleto_our_number
    receivable.boleto_digitable_line = digitable_line or receivable.boleto_digitable_line
    receivable.status = ReceivableStatus.BOLETO_ISSUED


def mark_paid(receivable: Receivable):
    receivable.status = ReceivableStatus.PAID
    receivable.paid_at = datetime.utcnow()
