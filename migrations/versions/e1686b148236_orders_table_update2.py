"""orders table update2

Revision ID: e1686b148236
Revises: dee7dabf96f0
Create Date: 2020-09-13 17:51:26.331491

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e1686b148236'
down_revision = 'dee7dabf96f0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('order', sa.Column('order_item', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'order', 'order_item', ['order_item'], ['id'])
    op.drop_column('order', 'OrderItem')
    op.create_foreign_key(None, 'order_item', 'user', ['customer'], ['id'])
    op.drop_column('order_item', 'purchase_date')
    op.create_foreign_key(None, 'product', 'retail_stores', ['store_id'], ['id'])
    op.create_foreign_key(None, 'product', 'category', ['category'], ['id'])
    op.drop_column('product', 'date')
    op.drop_column('product', 'item')
    op.drop_index('ix_retail_stores_store_name', table_name='retail_stores')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index('ix_retail_stores_store_name', 'retail_stores', ['store_name'], unique=False)
    op.add_column('product', sa.Column('item', sa.VARCHAR(length=64), nullable=True))
    op.add_column('product', sa.Column('date', sa.DATETIME(), nullable=True))
    op.drop_constraint(None, 'product', type_='foreignkey')
    op.drop_constraint(None, 'product', type_='foreignkey')
    op.add_column('order_item', sa.Column('purchase_date', sa.DATETIME(), nullable=True))
    op.drop_constraint(None, 'order_item', type_='foreignkey')
    op.add_column('order', sa.Column('OrderItem', sa.INTEGER(), nullable=True))
    op.drop_constraint(None, 'order', type_='foreignkey')
    op.drop_column('order', 'order_item')
    # ### end Alembic commands ###
