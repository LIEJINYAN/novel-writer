"""初始表结构创建

Revision ID: 0001
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # projects 表
    op.create_table(
        "projects",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("path", sa.String(1024), nullable=True),
        sa.Column("genre", sa.String(50), server_default=""),
        sa.Column("writing_method", sa.String(50), server_default="three-act"),
        sa.Column("status", sa.String(20), server_default="active"),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("target_words", sa.Integer(), server_default="0"),
        sa.Column("cover_image", sa.String(1024), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    
    # volumes 表
    op.create_table(
        "volumes",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("sort_order", sa.Integer(), server_default="0"),
        sa.Column("description", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    
    # chapters 表
    op.create_table(
        "chapters",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("volume_id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("chapter_number", sa.Integer(), server_default="1"),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("word_count", sa.Integer(), server_default="0"),
        sa.Column("status", sa.String(20), server_default="draft"),
        sa.Column("is_deleted", sa.Boolean(), server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["volume_id"], ["volumes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    
    # ai_providers 表
    op.create_table(
        "ai_providers",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("display_name", sa.String(100), nullable=True),
        sa.Column("api_key_encrypted", sa.String(1024), server_default=""),
        sa.Column("api_base", sa.String(1024), nullable=True),
        sa.Column("default_model", sa.String(100), server_default=""),
        sa.Column("temperature", sa.Float(), server_default="0.8"),
        sa.Column("max_tokens", sa.Integer(), server_default="4096"),
        sa.Column("is_enabled", sa.Boolean(), server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )


def downgrade() -> None:
    op.drop_table("ai_providers")
    op.drop_table("chapters")
    op.drop_table("volumes")
    op.drop_table("projects")
