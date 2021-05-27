"""add featured_asset_guid

Revision ID: 9b2a1efceeec
Revises: 8bea1f7d2e44
Create Date: 2021-05-20 15:46:22.561781

"""

# revision identifiers, used by Alembic.
revision = '9b2a1efceeec'
down_revision = '8bea1f7d2e44'

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils

import app
import app.extensions



def upgrade():
    """
    Upgrade Semantic Description:
        ENTER DESCRIPTION HERE
    """
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('sighting', schema=None) as batch_op:
        batch_op.add_column(sa.Column('featured_asset_guid', app.extensions.GUID(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    """
    Downgrade Semantic Description:
        ENTER DESCRIPTION HERE
    """
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('sighting', schema=None) as batch_op:
        batch_op.drop_column('featured_asset_guid')

    # ### end Alembic commands ###