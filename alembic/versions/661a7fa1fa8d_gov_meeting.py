"""gov_meeting

Revision ID: 661a7fa1fa8d
Revises: 2ffbd3369445
Create Date: 2020-06-29 21:03:57.650867

"""

# revision identifiers, used by Alembic.
revision = '661a7fa1fa8d'
down_revision = '2ffbd3369445'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('governance_meeting',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('meeting_date', sa.DateTime(), nullable=False),
    sa.Column('minutes', sa.Text(), nullable=False),
    sa.Column('agenda', sa.Text(), nullable=False),
    sa.Column('attendees', sa.Text(), nullable=False),
    sa.Column('track_id', sa.Integer(), nullable=True),
    sa.Column('creator_id', sa.Integer(), nullable=True),
    sa.Column('archived', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['creator_id'], ['user_user.id'], ),
    sa.ForeignKeyConstraint(['track_id'], ['content_track.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('governance_meetingstation',
    sa.Column('meeting_id', sa.Integer(), nullable=True),
    sa.Column('station_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['meeting_id'], ['governance_meeting.id'], ),
    sa.ForeignKeyConstraint(['station_id'], ['radio_station.id'], )
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('governance_meetingstation')
    op.drop_table('governance_meeting')
    ### end Alembic commands ###