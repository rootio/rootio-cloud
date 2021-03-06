"""dt_crtd_strm

Revision ID: 141d5446a745
Revises: 37a982c824d0
Create Date: 2017-08-24 17:06:46.910730

"""

# revision identifiers, used by Alembic.
revision = '141d5446a745'
down_revision = '37a982c824d0'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column(u'content_stream', sa.Column('date_created', sa.DateTime(timezone=True), server_default='now()', nullable=True))
    op.alter_column(u'content_stream', 'name',
               existing_type=sa.VARCHAR(length=100),
               nullable=True)
    op.alter_column(u'content_stream', 'uri',
               existing_type=sa.VARCHAR(length=200),
               nullable=True)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(u'content_stream', 'uri',
               existing_type=sa.VARCHAR(length=200),
               nullable=False)
    op.alter_column(u'content_stream', 'name',
               existing_type=sa.VARCHAR(length=100),
               nullable=False)
    op.drop_column(u'content_stream', 'date_created')
    ### end Alembic commands ###
