from datetime import datetime
from decimal import Decimal, InvalidOperation

from flask import Blueprint, flash, redirect, render_template, request, url_for
from sqlalchemy import or_

from ...extensions import db
from ...models import Address, Student

students_bp = Blueprint("students", __name__)


def _parse_date(value):
    if not value:
        return None
    return datetime.strptime(value, "%Y-%m-%d").date()


def _parse_decimal(value):
    try:
        normalized = (value or "0").replace(".", "").replace(",", ".")
        return Decimal(normalized)
    except InvalidOperation:
        raise ValueError("Valor de mensalidade invalido.")


def _student_from_form(student=None):
    student = student or Student()
    student.name = request.form.get("name", "").strip()
    student.document = request.form.get("document", "").strip()
    student.birth_date = _parse_date(request.form.get("birth_date"))
    student.payment_day = int(request.form.get("payment_day") or 1)
    student.monthly_fee = _parse_decimal(request.form.get("monthly_fee"))
    student.active = request.form.get("active") == "on"

    if not student.address:
        student.address = Address()
    student.address.zip_code = request.form.get("zip_code", "").strip()
    student.address.street = request.form.get("street", "").strip()
    student.address.district = request.form.get("district", "").strip()
    student.address.number = request.form.get("number", "").strip()
    student.address.complement = request.form.get("complement", "").strip()
    student.address.city = request.form.get("city", "").strip()
    student.address.state = request.form.get("state", "").strip().upper()[:2]

    if not student.name:
        raise ValueError("Informe o nome do aluno.")
    if not student.document:
        raise ValueError("Informe o CPF/CNPJ.")
    if student.payment_day < 1 or student.payment_day > 31:
        raise ValueError("O dia de pagamento deve ficar entre 1 e 31.")
    if student.monthly_fee <= 0:
        raise ValueError("A mensalidade deve ser maior que zero.")

    return student


@students_bp.get("/")
def index():
    query = request.args.get("q", "").strip()
    statement = db.select(Student).order_by(Student.name.asc())
    if query:
        statement = statement.where(
            or_(Student.name.ilike(f"%{query}%"), Student.document.ilike(f"%{query}%"))
        )
    students = db.session.scalars(statement).all()
    return render_template("students/index.html", students=students, query=query)


@students_bp.route("/novo", methods=["GET", "POST"])
def create():
    student = Student(active=True, payment_day=10)
    if request.method == "POST":
        try:
            student = _student_from_form(student)
            db.session.add(student)
            db.session.commit()
            flash("Aluno cadastrado com sucesso.", "success")
            return redirect(url_for("students.index"))
        except Exception as exc:
            db.session.rollback()
            flash(str(exc), "danger")
    return render_template("students/form.html", student=student)


@students_bp.route("/<int:student_id>/editar", methods=["GET", "POST"])
def edit(student_id):
    student = db.get_or_404(Student, student_id)
    if request.method == "POST":
        try:
            _student_from_form(student)
            db.session.commit()
            flash("Cadastro atualizado.", "success")
            return redirect(url_for("students.index"))
        except Exception as exc:
            db.session.rollback()
            flash(str(exc), "danger")
    return render_template("students/form.html", student=student)
