"""add deleted bool to uploads

Revision ID: 2150eb3e6577
Revises: 2d0a71aa0f59
Create Date: 2019-02-01 12:14:37.545683

"""

# revision identifiers, used by Alembic.
revision = '2150eb3e6577'
down_revision = '2d0a71aa0f59'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('content_uploads', sa.Column('deleted', sa.Boolean(), default=False))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('content_uploads', 'deleted')
    ### end Alembic commands ###
