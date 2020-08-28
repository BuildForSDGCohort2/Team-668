"""orders and products tables

Revision ID: c2699a6df077
Revises: e9097f50d162
Create Date: 2020-08-26 14:59:53.448668

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c2699a6df077'
down_revision = 'e9097f50d162'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('admin',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('fname', sa.String(length=64), nullable=True),
    sa.Column('lname', sa.String(length=64), nullable=True),
    sa.Column('email', sa.String(length=64), nullable=True),
    sa.Column('types', sa.String(length=64), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_admin_fname'), 'admin', ['fname'], unique=False)
    op.create_table('product',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('pname', sa.String(length=64), nullable=True),
    sa.Column('availabilty', sa.Integer(), nullable=True),
    sa.Column('category', sa.String(length=64), nullable=True),
    sa.Column('item', sa.String(length=64), nullable=True),
    sa.Column('picture', sa.Text(), nullable=True),
    sa.Column('description', sa.String(length=140), nullable=True),
    sa.Column('date', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_product_date'), 'product', ['date'], unique=False)
    op.create_index(op.f('ix_product_pname'), 'product', ['pname'], unique=False)
    op.create_table('order',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('pname', sa.String(length=64), nullable=True),
    sa.Column('qauntity', sa.Integer(), nullable=True),
    sa.Column('uid', sa.Integer(), nullable=True),
    sa.Column('odate', sa.DateTime(), nullable=True),
    sa.Column('ddate', sa.DateTime(), nullable=True),
    sa.Column('mobile', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['uid'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_order_odate'), 'order', ['odate'], unique=False)
    op.create_index(op.f('ix_order_pname'), 'order', ['pname'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_order_pname'), table_name='order')
    op.drop_index(op.f('ix_order_odate'), table_name='order')
    op.drop_table('order')
    op.drop_index(op.f('ix_product_pname'), table_name='product')
    op.drop_index(op.f('ix_product_date'), table_name='product')
    op.drop_table('product')
    op.drop_index(op.f('ix_admin_fname'), table_name='admin')
    op.drop_table('admin')
    # ### end Alembic commands ###
