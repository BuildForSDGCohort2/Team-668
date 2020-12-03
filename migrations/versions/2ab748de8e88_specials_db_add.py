"""Specials db add

Revision ID: 2ab748de8e88
Revises: 72015a554b93
Create Date: 2020-10-09 08:51:04.202216

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2ab748de8e88'
down_revision = '72015a554b93'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('specials',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('category_id', sa.Integer(), nullable=True),
    sa.Column('pname', sa.String(length=64), nullable=True),
    sa.Column('description', sa.String(length=140), nullable=True),
    sa.Column('prize', sa.Float(), nullable=True),
    sa.Column('availabilty', sa.Boolean(), nullable=True),
    sa.Column('picture', sa.String(length=150), nullable=True),
    sa.Column('store_id', sa.Integer(), nullable=True),
    sa.Column('discount', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['category_id'], ['category.id'], ),
    sa.ForeignKeyConstraint(['store_id'], ['retail_stores.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_specials_pname'), 'specials', ['pname'], unique=False)
    op.drop_column('aisles', 'image')
    op.create_foreign_key(None, 'order', 'customer_order_details', ['billing_address'], ['id'])
    op.add_column('order_item', sa.Column('special_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'order_item', 'specials', ['special_id'], ['id'])
    op.drop_constraint(None, 'product', type_='foreignkey')
    op.create_foreign_key(None, 'product', 'category', ['category_id'], ['id'])
    op.drop_column('product', 'category')
    op.add_column('user', sa.Column('is_admin', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'is_admin')
    op.add_column('product', sa.Column('category', sa.INTEGER(), nullable=True))
    op.drop_constraint(None, 'product', type_='foreignkey')
    op.create_foreign_key(None, 'product', 'category', ['category'], ['id'])
    op.drop_constraint(None, 'order_item', type_='foreignkey')
    op.drop_column('order_item', 'special_id')
    op.drop_constraint(None, 'order', type_='foreignkey')
    op.add_column('aisles', sa.Column('image', sa.VARCHAR(length=120), nullable=True))
    op.drop_index(op.f('ix_specials_pname'), table_name='specials')
    op.drop_table('specials')
    # ### end Alembic commands ###
