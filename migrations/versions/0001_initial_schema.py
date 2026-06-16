"""initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-06-16 15:50:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "students",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("document", sa.String(length=18), nullable=False),
        sa.Column("birth_date", sa.Date(), nullable=True),
        sa.Column("payment_day", sa.Integer(), nullable=False),
        sa.Column("monthly_fee", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("document"),
    )
    op.create_index(op.f("ix_students_document"), "students", ["document"], unique=False)
    op.create_index(op.f("ix_students_name"), "students", ["name"], unique=False)

    op.create_table(
        "addresses",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("zip_code", sa.String(length=9), nullable=True),
        sa.Column("street", sa.String(length=180), nullable=True),
        sa.Column("district", sa.String(length=120), nullable=True),
        sa.Column("number", sa.String(length=20), nullable=True),
        sa.Column("complement", sa.String(length=120), nullable=True),
        sa.Column("city", sa.String(length=120), nullable=True),
        sa.Column("state", sa.String(length=2), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "receivables",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("reference_month", sa.Date(), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=False),
        sa.Column("amount", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("boleto_generated", sa.Boolean(), nullable=False),
        sa.Column("boleto_generated_at", sa.DateTime(), nullable=True),
        sa.Column("boleto_our_number", sa.String(length=80), nullable=True),
        sa.Column("boleto_bank", sa.String(length=80), nullable=True),
        sa.Column("boleto_external_id", sa.String(length=120), nullable=True),
        sa.Column("boleto_digitable_line", sa.String(length=180), nullable=True),
        sa.Column("paid_at", sa.DateTime(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "student_id", "reference_month", name="uq_receivable_student_reference"
        ),
    )
    op.create_index(
        op.f("ix_receivables_due_date"), "receivables", ["due_date"], unique=False
    )
    op.create_index(
        op.f("ix_receivables_reference_month"),
        "receivables",
        ["reference_month"],
        unique=False,
    )

    op.create_table(
        "boleto_integration_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("receivable_id", sa.Integer(), nullable=True),
        sa.Column("provider", sa.String(length=80), nullable=False),
        sa.Column("action", sa.String(length=80), nullable=False),
        sa.Column("request_payload", sa.JSON(), nullable=True),
        sa.Column("response_payload", sa.JSON(), nullable=True),
        sa.Column("status_code", sa.Integer(), nullable=True),
        sa.Column("success", sa.Boolean(), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["receivable_id"], ["receivables.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("boleto_integration_logs")
    op.drop_index(op.f("ix_receivables_reference_month"), table_name="receivables")
    op.drop_index(op.f("ix_receivables_due_date"), table_name="receivables")
    op.drop_table("receivables")
    op.drop_table("addresses")
    op.drop_index(op.f("ix_students_name"), table_name="students")
    op.drop_index(op.f("ix_students_document"), table_name="students")
    op.drop_table("students")
