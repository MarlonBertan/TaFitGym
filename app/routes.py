from datetime import date

from flask import Blueprint, render_template
from sqlalchemy import func

from .extensions import db
from .models import Receivable, ReceivableStatus, Student

main_bp = Blueprint("main", __name__)


@main_bp.get("/")
def dashboard():
    today = date.today()
    month_start = today.replace(day=1)
    totals = {
        "students": db.session.scalar(db.select(func.count(Student.id))) or 0,
        "active_students": db.session.scalar(
            db.select(func.count(Student.id)).where(Student.active.is_(True))
        )
        or 0,
        "open": db.session.scalar(
            db.select(func.count(Receivable.id)).where(
                Receivable.status.in_(
                    [ReceivableStatus.OPEN, ReceivableStatus.BOLETO_ISSUED]
                )
            )
        )
        or 0,
        "month_amount": db.session.scalar(
            db.select(func.coalesce(func.sum(Receivable.amount), 0)).where(
                Receivable.reference_month == month_start
            )
        ),
    }

    overdue = db.session.scalars(
        db.select(Receivable)
        .join(Student)
        .where(
            Receivable.due_date < today,
            Receivable.status.in_([ReceivableStatus.OPEN, ReceivableStatus.BOLETO_ISSUED]),
        )
        .order_by(Receivable.due_date.asc())
        .limit(8)
    ).all()

    return render_template("dashboard.html", totals=totals, overdue=overdue)
