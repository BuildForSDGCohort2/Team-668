"""tables added

Revision ID: afdd038c7ff5
Revises: af9dfa76f44e
Create Date: 2020-09-09 09:19:39.076935

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'afdd038c7ff5'
down_revision = 'af9dfa76f44e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('customer_order_details',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('first_name', sa.String(length=64), nullable=True),
    sa.Column('last_name', sa.String(length=64), nullable=True),
    sa.Column('email', sa.String(length=64), nullable=True),
    sa.Column('address', sa.String(length=64), nullable=True),
    sa.Column('city', sa.String(length=64), nullable=True),
    sa.Column('mobile', sa.Integer(), nullable=True),
    sa.Column('odate', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_customer_order_details_first_name'), 'customer_order_details', ['first_name'], unique=False)
    op.create_index(op.f('ix_customer_order_details_odate'), 'customer_order_details', ['odate'], unique=False)
    op.create_table('supervisor',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('fname', sa.String(length=64), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_supervisor_fname'), 'supervisor', ['fname'], unique=False)
    op.create_table('category',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('store_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['store_id'], ['retail_stores.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_category_name'), 'category', ['name'], unique=False)
    op.create_table('order_item',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('order_client', sa.Integer(), nullable=True),
    sa.Column('product', sa.Integer(), nullable=True),
    sa.Column('prize', sa.Float(), nullable=True),
    sa.Column('quantity', sa.Integer(), nullable=True),
    sa.Column('purchase_date', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['order_client'], ['customer_order_details.id'], ),
    sa.ForeignKeyConstraint(['product'], ['product.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_index('ix_order_odate', table_name='order')
    op.drop_index('ix_order_pname', table_name='order')
    op.drop_table('order')
    op.add_column('product', sa.Column('store_id', sa.Integer(), nullable=True))
    op.drop_index('ix_product_date', table_name='product')
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
    op.create_index('ix_product_date', 'product', ['date'], unique=False)
    op.drop_column('product', 'store_id')
    op.create_table('order',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('pname', sa.VARCHAR(length=64), nullable=True),
    sa.Column('qauntity', sa.INTEGER(), nullable=True),
    sa.Column('uid', sa.INTEGER(), nullable=True),
    sa.Column('odate', sa.DATETIME(), nullable=True),
    sa.Column('ddate', sa.DATETIME(), nullable=True),
    sa.Column('mobile', sa.INTEGER(), nullable=True),
    sa.Column('prize', sa.INTEGER(), nullable=True),
    sa.ForeignKeyConstraint(['uid'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_order_pname', 'order', ['pname'], unique=False)
    op.create_index('ix_order_odate', 'order', ['odate'], unique=False)
    op.drop_table('order_item')
    op.drop_index(op.f('ix_category_name'), table_name='category')
    op.drop_table('category')
    op.drop_index(op.f('ix_supervisor_fname'), table_name='supervisor')
    op.drop_table('supervisor')
    op.drop_index(op.f('ix_customer_order_details_odate'), table_name='customer_order_details')
    op.drop_index(op.f('ix_customer_order_details_first_name'), table_name='customer_order_details')
    op.drop_table('customer_order_details')
    # ### end Alembic commands ###
