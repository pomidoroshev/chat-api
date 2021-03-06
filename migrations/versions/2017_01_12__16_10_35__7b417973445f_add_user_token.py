"""Add user token

Revision ID: 7b417973445f
Revises: 7940bc172ad5
Create Date: 2017-01-12 16:10:35.170563

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7b417973445f'
down_revision = '7940bc172ad5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('token', sa.String(length=40), nullable=True))
    op.create_index(op.f('ix_user_token'), 'user', ['token'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_user_token'), table_name='user')
    op.drop_column('user', 'token')
    # ### end Alembic commands ###
