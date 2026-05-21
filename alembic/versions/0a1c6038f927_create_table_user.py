"""create_table_user

Revision ID: 0a1c6038f927
Revises: 
Create Date: 2026-05-21 12:40:11.896309

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0a1c6038f927'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None




def upgrade():
    # Create status table
    op.create_table(
        'status',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create project table
    op.create_table(
        'project',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create images table
    op.create_table(
        'images',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('url', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('firstname', sa.String(100), nullable=False),
        sa.Column('lastname', sa.String(100), nullable=False),
        sa.Column('email', sa.String(200), nullable=False),
        sa.Column('password', sa.String(255), nullable=False),
        sa.Column('image_id', sa.Integer(), nullable=True),
        sa.Column('status_id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['image_id'], ['images.id']),
        sa.ForeignKeyConstraint(['status_id'], ['status.id']),
        sa.ForeignKeyConstraint(['project_id'], ['project.id'])
    )
    op.create_index('ix_users_id', 'users', ['id'])
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    # Create tokens table
    op.create_table(
        'tokens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('access_token', sa.String(500), nullable=False),
        sa.Column('refresh_token', sa.String(500), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'])
    )
    op.create_index('ix_tokens_id', 'tokens', ['id'])
    op.create_index('ix_tokens_access_token', 'tokens', ['access_token'], unique=True)
    op.create_index('ix_tokens_refresh_token', 'tokens', ['refresh_token'], unique=True)


def downgrade():
    op.drop_table('tokens')
    op.drop_table('users')
    op.drop_table('images')
    op.drop_table('project')
    op.drop_table('status')