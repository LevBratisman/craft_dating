"""add sex_target

Revision ID: c4812b56ff97
Revises: d3dcb3f5e2ea
Create Date: 2024-05-04 10:16:09.186967

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c4812b56ff97'
down_revision: Union[str, None] = 'd3dcb3f5e2ea'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('sex_target', sa.Integer(), nullable=True))
    op.drop_column('user', 'craft')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('craft', sa.VARCHAR(length=150), nullable=False))
    op.drop_column('user', 'sex_target')
    # ### end Alembic commands ###
