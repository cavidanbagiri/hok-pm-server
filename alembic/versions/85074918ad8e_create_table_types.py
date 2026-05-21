"""create_table_types

Revision ID: 85074918ad8e
Revises: 8218c87a3cf6
Create Date: 2026-05-21 22:24:23.887910

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '85074918ad8e'
down_revision: Union[str, Sequence[str], None] = '8218c87a3cf6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Create types table
    op.create_table(
        'types',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False, unique=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Add type_id column to type table
    op.add_column('type', sa.Column('type_id', sa.Integer(), nullable=False, server_default='1'))
    op.create_foreign_key('fk_type_types_id', 'type', 'types', ['type_id'], ['id'])

    # Remove server_default after adding column
    op.alter_column('type', 'type_id', server_default=None)


def downgrade():
    op.drop_constraint('fk_type_types_id', 'type', type_='foreignkey')
    op.drop_column('type', 'type_id')
    op.drop_table('types')