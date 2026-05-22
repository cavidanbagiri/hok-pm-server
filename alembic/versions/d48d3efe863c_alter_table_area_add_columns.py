"""alter_table_area_add_columns

Revision ID: d48d3efe863c
Revises: 85074918ad8e
Create Date: 2026-05-22 15:04:32.015431

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd48d3efe863c'
down_revision: Union[str, Sequence[str], None] = '85074918ad8e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 1. Add the new columns to the 'area' table
    # We set nullable=True initially to safe-handle existing rows in PostgreSQL
    op.add_column('area', sa.Column('doc_no', sa.String(), nullable=True))
    op.add_column('area', sa.Column('doc_rev', sa.String(), nullable=True))
    op.add_column('area', sa.Column('say_iso_no', sa.String(), nullable=True))

    # 2. OPTIONAL: If you have existing data, fill them with a default value before locking nullable=False
    op.execute("UPDATE area SET doc_no = 'N/A' WHERE doc_no IS NULL")
    op.execute("UPDATE area SET doc_rev = '0' WHERE doc_rev IS NULL")
    op.execute("UPDATE area SET say_iso_no = 'N/A' WHERE say_iso_no IS NULL")

    # 3. Enforce nullable=False to match your SQLAlchemy model rules
    op.alter_column('area', 'doc_no', nullable=False)
    op.alter_column('area', 'doc_rev', nullable=False)
    op.alter_column('area', 'say_iso_no', nullable=False)


def downgrade() -> None:
    # Rollback changes by dropping the columns in reverse order
    op.drop_column('area', 'say_iso_no')
    op.drop_column('area', 'doc_rev')
    op.drop_column('area', 'doc_no')