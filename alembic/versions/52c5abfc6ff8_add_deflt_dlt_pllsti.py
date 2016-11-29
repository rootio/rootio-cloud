"""add_deflt_dlt_pllstitm

Revision ID: 52c5abfc6ff8
Revises: 22cf3e320a08
Create Date: 2016-11-29 18:55:35.595296

"""

# revision identifiers, used by Alembic.
revision = '52c5abfc6ff8'
down_revision = '22cf3e320a08'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('content_musicplaylistitem', 'deleted')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('content_musicplaylistitem', sa.Column('deleted', sa.BOOLEAN(), nullable=True))
    ### end Alembic commands ###
