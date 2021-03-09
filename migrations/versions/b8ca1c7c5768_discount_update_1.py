"""discount update 1

Revision ID: b8ca1c7c5768
Revises: 8db71fa6b821
Create Date: 2020-09-28 16:57:11.954318

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b8ca1c7c5768'
down_revision = '8db71fa6b821'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('product', sa.Column('discount', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('product', 'discount')
    # ### end Alembic commands ###