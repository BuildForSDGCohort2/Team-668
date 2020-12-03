"""order table

Revision ID: 85889aa87716
Revises: 9ec078073c5d
Create Date: 2020-10-02 11:58:55.693643

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '85889aa87716'
down_revision = '9ec078073c5d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('order', sa.Column('billing_address', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'order', 'customer_order_details', ['billing_address'], ['id'])
    op.drop_constraint(None, 'product', type_='foreignkey')
    op.create_foreign_key(None, 'product', 'category', ['category_id'], ['id'])
    op.drop_column('product', 'category')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('product', sa.Column('category', sa.INTEGER(), nullable=True))
    op.drop_constraint(None, 'product', type_='foreignkey')
    op.create_foreign_key(None, 'product', 'category', ['category'], ['id'])
    op.drop_constraint(None, 'order', type_='foreignkey')
    op.drop_column('order', 'billing_address')
    # ### end Alembic commands ###
