"""add_created_dts

Revision ID: b7867a43c94
Revises: 78bed635e89
Create Date: 2017-08-23 16:16:00.857447

"""

# revision identifiers, used by Alembic.
revision = 'b7867a43c94'
down_revision = '78bed635e89'

from alembic import op
from sqlalchemy import func
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column(u'content_communitymenu', sa.Column('date_created', sa.DateTime(timezone=True), server_default=func.now(), nullable=True))
    op.alter_column(u'content_communitymenu', 'updated_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True, server_default=func.now())
    op.add_column(u'content_music', sa.Column('date_created', sa.DateTime(timezone=True), server_default=func.now(), nullable=True))
    op.add_column(u'content_musicalbum', sa.Column('date_created', sa.DateTime(timezone=True), server_default=func.now(), nullable=True))
    op.add_column(u'content_musicartist', sa.Column('date_created', sa.DateTime(timezone=True), server_default=func.now(), nullable=True))
    op.add_column(u'content_musicplaylist', sa.Column('date_created', sa.DateTime(timezone=True), server_default=func.now(), nullable=True))
    op.add_column(u'content_uploads', sa.Column('date_created', sa.DateTime(timezone=True), server_default=func.now(), nullable=True))
    op.alter_column(u'content_uploads', 'updated_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True, server_default=func.now())
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(u'content_uploads', 'updated_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False)
    op.drop_column(u'content_uploads', 'date_created')
    op.drop_column(u'content_musicplaylist', 'date_created')
    op.drop_column(u'content_musicartist', 'date_created')
    op.drop_column(u'content_musicalbum', 'date_created')
    op.drop_column(u'content_music', 'date_created')
    op.alter_column(u'content_communitymenu', 'updated_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False)
    op.drop_column(u'content_communitymenu', 'date_created')
    ### end Alembic commands ###
