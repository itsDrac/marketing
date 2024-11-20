"""Added CallRecord Table

Revision ID: 825f7fca290a
Revises: 7c7f5bfa21aa
Create Date: 2024-11-09 17:43:29.782995

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '825f7fca290a'
down_revision = '7c7f5bfa21aa'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('call_record',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('call_id', sa.String(length=20), nullable=False),
    sa.Column('duration', sa.Integer(), nullable=False),
    sa.Column('date', sa.DateTime(), nullable=False),
    sa.Column('summary', sa.Text(), nullable=False),
    sa.Column('number', sa.String(length=20), nullable=False),
    sa.Column('direction', sa.String(length=20), nullable=False),
    sa.Column('lead_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['lead_id'], ['lead.id'], name=op.f('fk_call_record_lead_id_lead')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_call_record'))
    )
    with op.batch_alter_table('call_record', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_call_record_lead_id'), ['lead_id'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('call_record', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_call_record_lead_id'))

    op.drop_table('call_record')
    # ### end Alembic commands ###
