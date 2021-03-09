"""Retail store db and Post form update

Revision ID: af9dfa76f44e
Revises: c2699a6df077
Create Date: 2020-08-27 15:09:19.127804

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'af9dfa76f44e'
down_revision = 'c2699a6df077'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('retail_stores',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('store_name', sa.String(length=64), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_retail_stores_store_name'), 'retail_stores', ['store_name'], unique=False)
    op.add_column('order', sa.Column('prize', sa.Integer(), nullable=True))
    op.add_column('product', sa.Column('prize', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('product', 'prize')
    op.drop_column('order', 'prize')
    op.drop_index(op.f('ix_retail_stores_store_name'), table_name='retail_stores')
    op.drop_table('retail_stores')
    # ### end Alembic commands ###