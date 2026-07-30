"""initial schema

Revision ID: 20260730_0001
Revises:
Create Date: 2026-07-30

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "20260730_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "diseases",
        sa.Column("acronym", sa.String(length=10), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint("acronym"),
    )
    op.create_table(
        "health_units",
        sa.Column("cnes_code", sa.String(length=15), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("district", sa.String(length=100), nullable=True),
        sa.Column("latitude", sa.Numeric(10, 8), nullable=False),
        sa.Column("longitude", sa.Numeric(11, 8), nullable=False),
        sa.Column("city_code", sa.String(length=10), nullable=True),
        sa.Column("unit_type", sa.String(length=50), nullable=True),
        sa.PrimaryKeyConstraint("cnes_code"),
    )
    op.create_table(
        "user",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("firebase_uid", sa.String(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("roles", postgresql.ARRAY(sa.String()), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "occurrences",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("disease_type", sa.String(length=10), nullable=False),
        sa.Column("health_unit_id", sa.String(length=15), nullable=False),
        sa.Column("notification_date", sa.Date(), nullable=False),
        sa.Column("city_id", sa.String(length=10), nullable=True),
        sa.Column("patient_age", sa.Integer(), nullable=True),
        sa.Column("patient_sex", sa.String(length=1), nullable=True),
        sa.Column("evolution", sa.String(length=50), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(["disease_type"], ["diseases.acronym"]),
        sa.ForeignKeyConstraint(["health_unit_id"], ["health_units.cnes_code"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("occurrences")
    op.drop_table("user")
    op.drop_table("health_units")
    op.drop_table("diseases")
