from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for

from ...extensions import db
from ...models import Receivable, ReceivableStatus, Student
from .services import generate_receivables, mark_boleto_generated, mark_paid

finance_bp = Blueprint("finance", __name__)


@finance_bp.get("/")
def index():
    status = request.args.get("status", "")
    statement = db.select(Receivable).join(Student).order_by(
        Receivable.due_date.asc(), Student.name.asc()
    )
    if status:
        statement = statement.where(Receivable.status == status)
    receivables = db.session.scalars(statement).all()
    return render_template(
        "finance/index.html",
        receivables=receivables,
        status=status,
        statuses=ReceivableStatus.LABELS,
    )


@finance_bp.route("/gerar", methods=["GET", "POST"])
def generate():
    students = db.session.scalars(
        db.select(Student).where(Student.active.is_(True)).order_by(Student.name.asc())
    ).all()
    if request.method == "POST":
        try:
            student = db.get_or_404(Student, int(request.form["student_id"]))
            start_month = datetime.strptime(request.form["start_month"], "%Y-%m").date()
            quantity = int(request.form.get("quantity") or 1)
            if quantity < 1 or quantity > 24:
                raise ValueError("Gere entre 1 e 24 mensalidades por vez.")
            created, skipped = generate_receivables(student, start_month, quantity)
            db.session.commit()
            flash(
                f"{len(created)} mensalidade(s) criada(s). {skipped} ja existia(m).",
                "success",
            )
            return redirect(url_for("finance.index"))
        except Exception as exc:
            db.session.rollback()
            flash(str(exc), "danger")
    return render_template("finance/generate.html", students=students)


@finance_bp.post("/<int:receivable_id>/boleto")
def boleto(receivable_id):
    receivable = db.get_or_404(Receivable, receivable_id)
    mark_boleto_generated(
        receivable,
        our_number=request.form.get("boleto_our_number"),
        digitable_line=request.form.get("boleto_digitable_line"),
    )
    db.session.commit()
    flash("Boleto marcado como gerado.", "success")
    return redirect(url_for("finance.index"))


@finance_bp.post("/<int:receivable_id>/pago")
def paid(receivable_id):
    receivable = db.get_or_404(Receivable, receivable_id)
    mark_paid(receivable)
    db.session.commit()
    flash("Mensalidade marcada como paga.", "success")
    return redirect(url_for("finance.index"))


@finance_bp.post("/<int:receivable_id>/cancelar")
def cancel(receivable_id):
    receivable = db.get_or_404(Receivable, receivable_id)
    receivable.status = ReceivableStatus.CANCELLED
    db.session.commit()
    flash("Mensalidade cancelada.", "warning")
    return redirect(url_for("finance.index"))
