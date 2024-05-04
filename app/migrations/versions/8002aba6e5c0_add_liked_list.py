"""add liked_list

Revision ID: 8002aba6e5c0
Revises: 5da218d9535a
Create Date: 2024-05-04 12:28:35.559505

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8002aba6e5c0'
down_revision: Union[str, None] = '5da218d9535a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('liked_users', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'liked_users')
    # ### end Alembic commands ###
