"""create_table_area_type_uom_stock_location

Revision ID: f29f547e9b8b
Revises: 64d6cf8ed57d
Create Date: 2026-05-21 16:42:46.973326

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f29f547e9b8b'
down_revision: Union[str, Sequence[str], None] = '64d6cf8ed57d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    # Create area table
    op.create_table(
        'area',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['project.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Create location table
    op.create_table(
        'location',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['project.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Create uom table
    op.create_table(
        'uom',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create type table
    # op.create_table(
    #     'type',
    #     sa.Column('id', sa.Integer(), nullable=False),
    #     sa.Column('name', sa.String(), nullable=False),
    #     sa.Column('sub_name', sa.String(), nullable=False),
    #     sa.Column('description', sa.String(), nullable=False),
    #     sa.Column('material', sa.String(), nullable=False),
    #     sa.Column('size_1', sa.String(), nullable=False),
    #     sa.Column('size_2', sa.String(), nullable=True),
    #     sa.Column('thickness_1', sa.String(), nullable=True),
    #     sa.Column('thickness_2', sa.String(), nullable=True),
    #     sa.PrimaryKeyConstraint('id')
    # )

    # # Create stock_data table
    # op.create_table(
    #     'stock_data',
    #     sa.Column('id', sa.Integer(), nullable=False),
    #     sa.Column('stock_code', sa.String(), nullable=False),
    #     sa.Column('alternative_id', sa.String(), nullable=True),
    #     sa.Column('old_code', sa.String(), nullable=True),
    #     sa.Column('comment', sa.String(), nullable=True),
    #     sa.Column('type_id', sa.Integer(), nullable=False),
    #     sa.Column('uom_id', sa.Integer(), nullable=False),
    #     sa.ForeignKeyConstraint(['type_id'], ['type.id']),
    #     sa.ForeignKeyConstraint(['uom_id'], ['uom.id']),
    #     sa.PrimaryKeyConstraint('id')
    # )


def downgrade():
    # op.drop_table('stock_data')
    # op.drop_table('type')
    op.drop_table('uom')
    op.drop_table('location')
    op.drop_table('area')