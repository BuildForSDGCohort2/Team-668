"""product table update 2

Revision ID: e2d9db28675c
Revises: 91bf077aa15c
Create Date: 2020-09-30 19:20:41.739300

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e2d9db28675c'
down_revision = '91bf077aa15c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'product', type_='foreignkey')
    op.create_foreign_key(None, 'product', 'category', ['category_id'], ['id'])
    op.drop_column('product', 'category')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('product', sa.Column('category', sa.INTEGER(), nullable=True))
    op.drop_constraint(None, 'product', type_='foreignkey')
    op.create_foreign_key(None, 'product', 'category', ['category'], ['id'])
    # ### end Alembic commands ###