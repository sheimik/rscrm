"""add contact info to objects

Revision ID: 1e4d4483d8f3
Revises: 0885dbc03582
Create Date: 2025-02-14 12:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "1e4d4483d8f3"
down_revision = "0885dbc03582"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "objects",
        sa.Column("contact_name", sa.String(length=255), nullable=True),
    )
    op.add_column(
        "objects",
        sa.Column("contact_phone", sa.String(length=32), nullable=True),
    )
    op.create_index(
        "ix_objects_contact_phone",
        "objects",
        ["contact_phone"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_objects_contact_phone", table_name="objects")
    op.drop_column("objects", "contact_phone")
    op.drop_column("objects", "contact_name")
