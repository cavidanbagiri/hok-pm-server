"""alter_table_type

Revision ID: 8218c87a3cf6
Revises: f29f547e9b8b
Create Date: 2026-05-21 21:06:15.292022

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8218c87a3cf6'
down_revision: Union[str, Sequence[str], None] = 'f29f547e9b8b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Create subtype table
    op.create_table(
        'subtype',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False, unique=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create size_1 table
    op.create_table(
        'size_1',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False, unique=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create size_2 table
    op.create_table(
        'size_2',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False, unique=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create material table
    op.create_table(
        'material',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False, unique=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create description table
    op.create_table(
        'description',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False, unique=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Drop old type table and recreate with foreign keys
    # op.drop_table('type')

    op.create_table(
        'type',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('subtype_id', sa.Integer(), nullable=False),
        sa.Column('size1_id', sa.Integer(), nullable=False),
        sa.Column('size2_id', sa.Integer(), nullable=True),
        sa.Column('material_id', sa.Integer(), nullable=False),
        sa.Column('description_id', sa.Integer(), nullable=False),
        sa.Column('thickness_1', sa.String(), nullable=True),
        sa.Column('thickness_2', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['subtype_id'], ['subtype.id']),
        sa.ForeignKeyConstraint(['size1_id'], ['size_1.id']),
        sa.ForeignKeyConstraint(['size2_id'], ['size_2.id']),
        sa.ForeignKeyConstraint(['material_id'], ['material.id']),
        sa.ForeignKeyConstraint(['description_id'], ['description.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Create stock_data table
    op.create_table(
        'stock_data',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('stock_code', sa.String(), nullable=False),
        sa.Column('alternative_id', sa.String(), nullable=True),
        sa.Column('old_code', sa.String(), nullable=True),
        sa.Column('comment', sa.String(), nullable=True),
        sa.Column('type_id', sa.Integer(), nullable=False),
        sa.Column('uom_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['type_id'], ['type.id']),
        sa.ForeignKeyConstraint(['uom_id'], ['uom.id']),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('type')
    op.drop_table('description')
    op.drop_table('material')
    op.drop_table('size_2')
    op.drop_table('size_1')
    op.drop_table('subtype')

    # Recreate old type table
    op.create_table(
        'type',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('sub_name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=False),
        sa.Column('material', sa.String(), nullable=False),
        sa.Column('size_1', sa.String(), nullable=False),
        sa.Column('size_2', sa.String(), nullable=True),
        sa.Column('thickness_1', sa.String(), nullable=True),
        sa.Column('thickness_2', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )