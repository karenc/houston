"""empty message

Revision ID: a042326c4b51
Revises: 43e8c8669945
Create Date: 2020-09-11 13:39:33.457156

"""

# revision identifiers, used by Alembic.
revision = 'a042326c4b51'
down_revision = '43e8c8669945'

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils

import app
import app.extensions



def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('submission', schema=None) as batch_op:
        batch_op.add_column(sa.Column('major_type', sa.Enum('filesystem', 'archive', 'service', 'test', 'unknown', 'error', 'reject', name='submissionmajortype'), nullable=False))
        batch_op.create_index(batch_op.f('ix_submission_major_type'), ['major_type'], unique=False)
        batch_op.drop_index('ix_submission_submission_major_type')
        batch_op.drop_column('submission_major_type')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('submission', schema=None) as batch_op:
        batch_op.add_column(sa.Column('submission_major_type', sa.VARCHAR(length=10), nullable=False))
        batch_op.create_index('ix_submission_submission_major_type', ['submission_major_type'], unique=False)
        batch_op.drop_index(batch_op.f('ix_submission_major_type'))
        batch_op.drop_column('major_type')

    # ### end Alembic commands ###