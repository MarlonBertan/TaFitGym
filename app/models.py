from datetime import date, datetime
from decimal import Decimal

from .extensions import db


class TimestampMixin:
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


class Student(TimestampMixin, db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160), nullable=False, index=True)
    document = db.Column(db.String(18), nullable=False, unique=True, index=True)
    birth_date = db.Column(db.Date)
    payment_day = db.Column(db.Integer, nullable=False)
    monthly_fee = db.Column(db.Numeric(10, 2), nullable=False)
    active = db.Column(db.Boolean, default=True, nullable=False)

    address = db.relationship(
        "Address", back_populates="student", uselist=False, cascade="all, delete-orphan"
    )
    receivables = db.relationship(
        "Receivable", back_populates="student", cascade="all, delete-orphan"
    )

    def current_fee(self):
        return self.monthly_fee or Decimal("0.00")


class Address(TimestampMixin, db.Model):
    __tablename__ = "addresses"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(
        db.Integer, db.ForeignKey("students.id", ondelete="CASCADE"), nullable=False
    )
    zip_code = db.Column(db.String(9))
    street = db.Column(db.String(180))
    district = db.Column(db.String(120))
    number = db.Column(db.String(20))
    complement = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(2))

    student = db.relationship("Student", back_populates="address")


class ReceivableStatus:
    OPEN = "open"
    BOLETO_ISSUED = "boleto_issued"
    PAID = "paid"
    CANCELLED = "cancelled"

    LABELS = {
        OPEN: "Em aberto",
        BOLETO_ISSUED: "Boleto gerado",
        PAID: "Pago",
        CANCELLED: "Cancelado",
    }


class Receivable(TimestampMixin, db.Model):
    __tablename__ = "receivables"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    reference_month = db.Column(db.Date, nullable=False, index=True)
    due_date = db.Column(db.Date, nullable=False, index=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(20), default=ReceivableStatus.OPEN, nullable=False)
    boleto_generated = db.Column(db.Boolean, default=False, nullable=False)
    boleto_generated_at = db.Column(db.DateTime)
    boleto_our_number = db.Column(db.String(80))
    boleto_bank = db.Column(db.String(80), default="Banco do Brasil")
    boleto_external_id = db.Column(db.String(120))
    boleto_digitable_line = db.Column(db.String(180))
    paid_at = db.Column(db.DateTime)
    notes = db.Column(db.Text)

    student = db.relationship("Student", back_populates="receivables")

    __table_args__ = (
        db.UniqueConstraint(
            "student_id", "reference_month", name="uq_receivable_student_reference"
        ),
    )

    @property
    def status_label(self):
        return ReceivableStatus.LABELS.get(self.status, self.status)

    @property
    def is_overdue(self):
        return self.status in {
            ReceivableStatus.OPEN,
            ReceivableStatus.BOLETO_ISSUED,
        } and self.due_date < date.today()


class BoletoIntegrationLog(TimestampMixin, db.Model):
    __tablename__ = "boleto_integration_logs"

    id = db.Column(db.Integer, primary_key=True)
    receivable_id = db.Column(db.Integer, db.ForeignKey("receivables.id"))
    provider = db.Column(db.String(80), nullable=False, default="Banco do Brasil")
    action = db.Column(db.String(80), nullable=False)
    request_payload = db.Column(db.JSON)
    response_payload = db.Column(db.JSON)
    status_code = db.Column(db.Integer)
    success = db.Column(db.Boolean, nullable=False, default=False)
    error_message = db.Column(db.Text)
