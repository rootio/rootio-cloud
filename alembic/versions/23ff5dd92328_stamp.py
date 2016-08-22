"""stamp

Revision ID: 23ff5dd92328
Revises: 5769f7c6759c
Create Date: 2014-04-28 23:55:47.538054

"""

# revision identifiers, used by Alembic.
revision = '23ff5dd92328'
down_revision = '5769f7c6759c'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('telephony_gateway', sa.Column('is_goip', sa.Boolean(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('telephony_gateway', 'is_goip')
    ### end Alembic commands ###
