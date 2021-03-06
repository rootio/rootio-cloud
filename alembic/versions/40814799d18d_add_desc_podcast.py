"""add_desc_podcast

Revision ID: 40814799d18d
Revises: cdf3cfea28c
Create Date: 2016-11-14 17:12:45.893554

"""

# revision identifiers, used by Alembic.
revision = '40814799d18d'
down_revision = 'cdf3cfea28c'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('content_podcast', sa.Column('description', sa.String(length=100), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('content_podcast', 'description')
    ### end Alembic commands ###
