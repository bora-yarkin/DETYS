"""empty message

Revision ID: 5dbf1ea664a4
Revises: aeb51f6410d7
Create Date: 2024-12-25 23:15:02.418808

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5dbf1ea664a4'
down_revision = 'aeb51f6410d7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('club_message',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('club_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['club_id'], ['clubs.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('club_message')
    # ### end Alembic commands ###
