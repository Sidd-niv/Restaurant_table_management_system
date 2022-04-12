"""database change records

Revision ID: 3c94d4ea33b4
Revises: 
Create Date: 2022-04-02 12:48:02.930794

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3c94d4ea33b4'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("Customer_login", sa.Column('cancel charges', sa.Integer, nullable=True))
    pass



def downgrade():
    op.drop_column("Customer_login", sa.Column('cancel charges', sa.Integer, nullable=True))
    pass
