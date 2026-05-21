"""add_column_project_model_country_code

Revision ID: 64d6cf8ed57d
Revises: 0a1c6038f927
Create Date: 2026-05-21 15:12:54.440857

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '64d6cf8ed57d'
down_revision: Union[str, Sequence[str], None] = '0a1c6038f927'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Add new columns to project table
    op.add_column('project', sa.Column('country', sa.String(), nullable=False, server_default=''))
    op.add_column('project', sa.Column('code', sa.String(), nullable=False, server_default=''))

    # Remove server_default after adding columns (optional)
    op.alter_column('project', 'country', server_default=None)
    op.alter_column('project', 'code', server_default=None)


def downgrade():
    # Remove columns
    op.drop_column('project', 'country')
    op.drop_column('project', 'code')