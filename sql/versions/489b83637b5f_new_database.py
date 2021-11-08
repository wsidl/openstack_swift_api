"""new database

Revision ID: 489b83637b5f
Revises: 
Create Date: 2021-10-24 12:09:24.534099

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "489b83637b5f"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "objects",
        sa.Column("o_id", sa.Integer, autoincrement=True, primary_key=True),
        sa.Column("o_hash", sa.Text, unique=True),
        sa.Column("o_name", sa.Text, unique=True),
    )
    op.create_table(
        "metadata",
        sa.Column("o_id", sa.Integer, sa.ForeignKey("objects.o_id")),
        sa.Column("m_key", sa.String(50), index=True),
        sa.Column("m_value", sa.String(50)),
    )
    op.create_index("m_key_value_idx", "metadata", ["m_key", "m_value"])
    op.create_index("m_okv_idx", "metadata", ["o_id", "m_key", "m_value"], unique=True)


def downgrade():
    op.drop_index("m_okv_idx")
    op.drop_index("m_key_value_idx")
    op.drop_table("metadata")
    op.drop_table("objects")
