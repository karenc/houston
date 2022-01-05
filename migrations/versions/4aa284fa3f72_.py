"""empty message

Revision ID: 4aa284fa3f72
Revises: 973184c68d5e
Create Date: 2021-12-28 17:14:56.872762

"""

# revision identifiers, used by Alembic.
revision = '4aa284fa3f72'
down_revision = '973184c68d5e'

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
        batch_op.add_column(sa.Column('time_guid', app.extensions.GUID(), nullable=False))
        batch_op.create_index(batch_op.f('ix_sighting_time_guid'), ['time_guid'], unique=False)
        batch_op.create_foreign_key(batch_op.f('fk_sighting_time_guid_complex_date_time'), 'complex_date_time', ['time_guid'], ['guid'])

    # ### end Alembic commands ###


def downgrade():
    """
    Downgrade Semantic Description:
        ENTER DESCRIPTION HERE
    """
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('sighting', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('fk_sighting_time_guid_complex_date_time'), type_='foreignkey')
        batch_op.drop_index(batch_op.f('ix_sighting_time_guid'))
        batch_op.drop_column('time_guid')

    # ### end Alembic commands ###
