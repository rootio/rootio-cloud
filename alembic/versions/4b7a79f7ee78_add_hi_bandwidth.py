"""add_hi_bandwidth

Revision ID: 4b7a79f7ee78
Revises: 293edef43cf6
Create Date: 2018-10-15 14:58:36.458169

"""

# revision identifiers, used by Alembic.
revision = '4b7a79f7ee78'
down_revision = '293edef43cf6'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('radio_station', sa.Column('is_high_bandwidth', sa.Boolean(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('radio_station', 'is_high_bandwidth')
    ### end Alembic commands ###
