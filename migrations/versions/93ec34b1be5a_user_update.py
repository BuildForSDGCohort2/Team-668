"""user update

Revision ID: 93ec34b1be5a
Revises: c41969b657d7
Create Date: 2020-09-28 14:23:11.313202

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '93ec34b1be5a'
down_revision = 'c41969b657d7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_foreign_key(None, 'category', 'aisles', ['aisles_id'], ['id'])
    op.create_foreign_key(None, 'order', 'order_item', ['order_item'], ['id'])
    op.drop_column('order', 'OrderItem')
    op.create_foreign_key(None, 'order_item', 'user', ['customer'], ['id'])
    op.drop_column('order_item', 'purchase_date')
    op.create_foreign_key(None, 'product', 'category', ['category'], ['id'])
    op.create_foreign_key(None, 'product', 'retail_stores', ['store_id'], ['id'])
    op.drop_column('product', 'item')
    op.drop_column('product', 'date')
    op.drop_index('ix_retail_stores_store_name', table_name='retail_stores')
    op.add_column('user', sa.Column('image', sa.String(length=140), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'image')
    op.create_index('ix_retail_stores_store_name', 'retail_stores', ['store_name'], unique=False)
    op.add_column('product', sa.Column('date', sa.DATETIME(), nullable=True))
    op.add_column('product', sa.Column('item', sa.VARCHAR(length=64), nullable=True))
    op.drop_constraint(None, 'product', type_='foreignkey')
    op.drop_constraint(None, 'product', type_='foreignkey')
    op.add_column('order_item', sa.Column('purchase_date', sa.DATETIME(), nullable=True))
    op.drop_constraint(None, 'order_item', type_='foreignkey')
    op.add_column('order', sa.Column('OrderItem', sa.INTEGER(), nullable=True))
    op.drop_constraint(None, 'order', type_='foreignkey')
    op.drop_constraint(None, 'category', type_='foreignkey')
    # ### end Alembic commands ###