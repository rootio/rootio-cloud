"""change status in scheduledProgram

Revision ID: 0937f7e9feb5
Revises: 1ae1c8228945
Create Date: 2019-09-18 21:46:02.754520

"""

# revision identifiers, used by Alembic.
revision = '0937f7e9feb5'
down_revision = '1ae1c8228945'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('radio_scheduledprogram', 'status',
               existing_type=sa.BOOLEAN(),
               type_=sa.Integer(),
               existing_nullable=True,
               postgresql_using='status::integer')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('radio_scheduledprogram', 'status',
               existing_type=sa.Integer(),
               type_=sa.BOOLEAN(),
               existing_nullable=True)
    ### end Alembic commands ###

