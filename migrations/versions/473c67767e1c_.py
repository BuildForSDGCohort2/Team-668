"""empty message

Revision ID: 473c67767e1c
Revises: e901c3b4cd08
Create Date: 2020-12-03 11:43:27.027477

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '473c67767e1c'
down_revision = 'e901c3b4cd08'
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
    sa.Column('ship_add', sa.Boolean(), nullable=True),
    sa.Column('odate', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_customer_order_details_first_name'), 'customer_order_details', ['first_name'], unique=False)
    op.create_index(op.f('ix_customer_order_details_odate'), 'customer_order_details', ['odate'], unique=False)
    op.create_table('retail_stores',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('store_name', sa.String(length=64), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=True),
    sa.Column('email', sa.String(length=120), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.Column('about_me', sa.String(length=140), nullable=True),
    sa.Column('image', sa.String(length=140), nullable=True),
    sa.Column('last_seen', sa.DateTime(), nullable=True),
    sa.Column('token', sa.String(length=32), nullable=True),
    sa.Column('token_expiration', sa.DateTime(), nullable=True),
    sa.Column('is_admin', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    op.create_index(op.f('ix_user_token'), 'user', ['token'], unique=True)
    op.create_index(op.f('ix_user_username'), 'user', ['username'], unique=True)
    op.create_table('aisles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('store_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['store_id'], ['retail_stores.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_aisles_name'), 'aisles', ['name'], unique=False)
    op.create_table('followers',
    sa.Column('follower_id', sa.Integer(), nullable=True),
    sa.Column('followed_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['followed_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['follower_id'], ['user.id'], )
    )
    op.create_table('post',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('body', sa.String(length=140), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_post_timestamp'), 'post', ['timestamp'], unique=False)
    op.create_table('category',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('store_id', sa.Integer(), nullable=True),
    sa.Column('aisles_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['aisles_id'], ['aisles.id'], ),
    sa.ForeignKeyConstraint(['store_id'], ['retail_stores.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_category_name'), 'category', ['name'], unique=False)
    op.create_table('product',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('category_id', sa.Integer(), nullable=True),
    sa.Column('pname', sa.String(length=64), nullable=True),
    sa.Column('description', sa.String(length=140), nullable=True),
    sa.Column('prize', sa.Float(), nullable=True),
    sa.Column('availabilty', sa.Boolean(), nullable=True),
    sa.Column('picture', sa.String(length=150), nullable=True),
    sa.Column('store_id', sa.Integer(), nullable=True),
    sa.Column('discount', sa.Integer(), nullable=True),
    sa.Column('special', sa.String(length=60), nullable=True),
    sa.ForeignKeyConstraint(['category_id'], ['category.id'], ),
    sa.ForeignKeyConstraint(['store_id'], ['retail_stores.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_product_pname'), 'product', ['pname'], unique=False)
    op.create_table('order_item',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('order_client', sa.Integer(), nullable=True),
    sa.Column('customer', sa.Integer(), nullable=True),
    sa.Column('product', sa.Integer(), nullable=True),
    sa.Column('prize', sa.Float(), nullable=True),
    sa.Column('quantity', sa.Integer(), nullable=True),
    sa.Column('order_item_created_date', sa.DateTime(), nullable=True),
    sa.Column('ordered', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['customer'], ['user.id'], ),
    sa.ForeignKeyConstraint(['order_client'], ['customer_order_details.id'], ),
    sa.ForeignKeyConstraint(['product'], ['product.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('order',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('customer', sa.Integer(), nullable=True),
    sa.Column('order_item', sa.Integer(), nullable=True),
    sa.Column('start_date', sa.DateTime(), nullable=True),
    sa.Column('order_date', sa.DateTime(), nullable=True),
    sa.Column('ordered', sa.Boolean(), nullable=True),
    sa.Column('billing_address', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['billing_address'], ['customer_order_details.id'], ),
    sa.ForeignKeyConstraint(['customer'], ['user.id'], ),
    sa.ForeignKeyConstraint(['order_item'], ['order_item.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('products',
    sa.Column('order_item_id', sa.Integer(), nullable=True),
    sa.Column('order_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['order_id'], ['order.id'], ),
    sa.ForeignKeyConstraint(['order_item_id'], ['order_item.id'], )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('products')
    op.drop_table('order')
    op.drop_table('order_item')
    op.drop_index(op.f('ix_product_pname'), table_name='product')
    op.drop_table('product')
    op.drop_index(op.f('ix_category_name'), table_name='category')
    op.drop_table('category')
    op.drop_index(op.f('ix_post_timestamp'), table_name='post')
    op.drop_table('post')
    op.drop_table('followers')
    op.drop_index(op.f('ix_aisles_name'), table_name='aisles')
    op.drop_table('aisles')
    op.drop_index(op.f('ix_user_username'), table_name='user')
    op.drop_index(op.f('ix_user_token'), table_name='user')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')
    op.drop_table('retail_stores')
    op.drop_index(op.f('ix_customer_order_details_odate'), table_name='customer_order_details')
    op.drop_index(op.f('ix_customer_order_details_first_name'), table_name='customer_order_details')
    op.drop_table('customer_order_details')
    # ### end Alembic commands ###
