"""初始化应用级数据库表结构。

当前表结构由 AppBase.metadata.create_all 自动创建，
此迁移仅用于标记初始版本，不执行实际 DDL。

Revision ID: 0001
Revises: 
Create Date: 2026-07-03 16:00:00
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """项目级表由 ProjectBase.metadata.create_all 自动创建，此处无需操作。"""
    pass


def downgrade() -> None:
    """降级不做任何操作。"""
    pass
