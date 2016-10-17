"""remove_redundant_relationship

Revision ID: 1e09e4b69a8c
Revises: 239d8482a01e
Create Date: 2016-10-14 17:55:24.751243

"""

# revision identifiers, used by Alembic.
revision = '1e09e4b69a8c'
down_revision = '239d8482a01e'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('radio_content_type')
    op.add_column('onair_program', sa.Column('episode_id', sa.Integer(), nullable=True))
    op.add_column('onair_program', sa.Column('scheduledprogram_id', sa.Integer(), nullable=True))
    op.drop_column('onair_program', 'scheduledepisode_id')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('onair_program', sa.Column('scheduledepisode_id', sa.INTEGER(), nullable=True))
    op.drop_column('onair_program', 'scheduledprogram_id')
    op.drop_column('onair_program', 'episode_id')
    op.create_table('radio_content_type',
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('id', sa.INTEGER(), server_default="nextval('radio_content_type_id_seq'::regclass)", nullable=False),
    sa.Column('name', sa.VARCHAR(length=100), autoincrement=False, nullable=False),
    sa.Column('description', sa.TEXT(), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name=u'radio_content_type_pkey')
    )
    ### end Alembic commands ###