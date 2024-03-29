"""empty message

Revision ID: 2566a1eba0fb
Revises: 
Create Date: 2024-02-07 13:58:49.597360

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2566a1eba0fb'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('is_admin', sa.Boolean(), nullable=True))
    op.add_column('users', sa.Column('is_supplier', sa.Boolean(), nullable=True))
    op.add_column('users', sa.Column('is_customer', sa.Boolean(), nullable=True))
    op.drop_column('users', 'role')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('role', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_column('users', 'is_customer')
    op.drop_column('users', 'is_supplier')
    op.drop_column('users', 'is_admin')
    # ### end Alembic commands ###
