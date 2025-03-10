"""Added Campaign table

Revision ID: e6e7a5c23529
Revises: 1619a711a264
Create Date: 2024-10-17 23:45:46.520211

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e6e7a5c23529'
down_revision = '1619a711a264'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('campaign',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('token', sa.String(length=256), nullable=True),
    sa.Column('client_id', sa.Integer(), nullable=False),
    sa.Column('end_date', sa.Date(), nullable=True),
    sa.Column('start_date', sa.Date(), nullable=False),
    sa.ForeignKeyConstraint(['client_id'], ['client.id'], name=op.f('fk_campaign_client_id_client')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_campaign'))
    )
    with op.batch_alter_table('campaign', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_campaign_client_id'), ['client_id'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('campaign', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_campaign_client_id'))

    op.drop_table('campaign')
    # ### end Alembic commands ###
