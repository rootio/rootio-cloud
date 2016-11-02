"""removing_host_table

Revision ID: 35ced00df34d
Revises: 2b191eb9d05c
Create Date: 2016-10-31 14:04:25.324578

"""

# revision identifiers, used by Alembic.
revision = '35ced00df34d'
down_revision = '2b191eb9d05c'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('radio_hostlanguage')
    op.drop_table('radio_host')
    #op.drop_table('radio_hostlanguage')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('radio_hostlanguage',
    sa.Column('language_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('host_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['host_id'], [u'radio_host.id'], name=u'radio_hostlanguage_host_id_fkey'),
    sa.ForeignKeyConstraint(['language_id'], [u'radio_language.id'], name=u'radio_hostlanguage_language_id_fkey'),
    sa.PrimaryKeyConstraint()
    )
    op.create_table('radio_host',
    sa.Column('id', sa.INTEGER(), server_default="nextval('radio_host_id_seq'::regclass)", nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('title', sa.VARCHAR(length=8), autoincrement=False, nullable=True),
    sa.Column('firstname', sa.VARCHAR(length=100), autoincrement=False, nullable=True),
    sa.Column('middlename', sa.VARCHAR(length=100), autoincrement=False, nullable=True),
    sa.Column('lastname', sa.VARCHAR(length=100), autoincrement=False, nullable=True),
    sa.Column('email', sa.VARCHAR(length=100), autoincrement=False, nullable=True),
    sa.Column('additionalcontact', sa.VARCHAR(length=100), autoincrement=False, nullable=True),
    sa.Column('phone_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('gender_code', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('privacy_code', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['phone_id'], [u'telephony_phonenumber.id'], name=u'radio_host_phone_id_fkey'),
    sa.PrimaryKeyConstraint('id', name=u'radio_host_pkey')
    )
    ### end Alembic commands ###