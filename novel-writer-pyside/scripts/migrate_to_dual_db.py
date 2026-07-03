#!/usr/bin/env python3
"""将旧单库数据迁移到双层数据库架构。

用法：
    python scripts/migrate_to_dual_db.py [--db 应用级DB路径]

从旧 `novel_writer.db` 中按 project_id 分组，
每个项目导出为独立的 `.novel/project.db`。

注意事项：
- 先备份 novel_writer.db
- 迁移后旧库保留，但项目级表会被清空
- 迁移后需要手动验证数据完整性
"""
import sys
import os
import sqlite3
from pathlib import Path

# 确保项目根目录在 sys.path 中
sys.path.insert(0, str(Path(__file__).parent.parent))


APP_TABLES = [
    "app_config", "projects", "ai_providers",
    "ai_conversations", "plugins",
]
PROJECT_TABLES = [
    "project_info", "volumes", "chapters", "characters",
    "character_states", "character_appearances", "plot_nodes",
    "foreshadowings", "conflicts", "relationships", "factions",
    "faction_members", "relationship_history", "timeline_events",
    "validation_rules", "world_settings", "writing_method_config",
    "writing_statistics",
]


def get_column_names(conn: sqlite3.Connection, table: str) -> list[str]:
    """获取表的所有列名。"""
    cursor = conn.execute(f"PRAGMA table_info({table})")
    return [row[1] for row in cursor.fetchall()]


def migrate_project(conn: sqlite3.Connection, project_id: int,
                    project_name: str, project_path: str):
    """将一个项目的数据从旧库迁移到独立的 project.db。"""
    project_dir = Path(project_path) if project_path else Path(".")
    project_db_path = project_dir / ".novel" / "project.db"

    print(f"  迁移项目 [{project_id}]: {project_name}")
    print(f"    目标: {project_db_path}")

    # 创建项目目录
    project_db_path.parent.mkdir(parents=True, exist_ok=True)

    # 创建项目级 DB
    proj_conn = sqlite3.connect(str(project_db_path))
    proj_conn.execute("PRAGMA journal_mode=WAL")
    proj_conn.execute("PRAGMA foreign_keys=ON")

    # 获取旧库的列名映射
    old_columns: dict[str, list[str]] = {}
    for table in PROJECT_TABLES:
        try:
            old_columns[table] = get_column_names(conn, table)
        except Exception:
            pass

    # 从当前代码导入并创建表
    from models.database import ProjectBase
    from sqlalchemy import create_engine
    engine = create_engine(f"sqlite:///{project_db_path}")
    ProjectBase.metadata.create_all(engine)

    # 逐表迁移（移除 project_id 列）
    for table in PROJECT_TABLES:
        old_cols = old_columns.get(table, [])
        if not old_cols:
            continue

        # 去掉 project_id 列
        projectless_cols = [c for c in old_cols if c != "project_id"]
        if not projectless_cols:
            continue

        col_list = ", ".join(projectless_cols)
        placeholders = ", ".join("?" for _ in projectless_cols)

        try:
            # 从旧库 SELECT
            rows = conn.execute(
                f"SELECT {col_list} FROM {table} WHERE project_id = ?",
                (project_id,)
            ).fetchall()

            if rows:
                # 写入项目 DB
                for row in rows:
                    stripped = []
                    for col_name in projectless_cols:
                        idx = old_cols.index(col_name)
                        stripped.append(row[idx])
                    proj_conn.execute(
                        f"INSERT INTO {table} ({col_list}) VALUES ({placeholders})",
                        stripped,
                    )
                proj_conn.commit()
                print(f"    ✓ {table}: {len(rows)} 条记录")
        except Exception as e:
            print(f"    ✗ {table}: 跳过 ({e})")
            proj_conn.rollback()

    proj_conn.close()

    # 创建 project_info 记录（从旧 projects 表迁移）
    try:
        row = conn.execute(
            "SELECT name, description, genre, writing_method, status, "
            "created_at, updated_at "
            "FROM projects WHERE id = ?", (project_id,)
        ).fetchone()
        if row:
            proj_conn2 = sqlite3.connect(str(project_db_path))
            proj_conn2.execute(
                "INSERT INTO project_info (name, description, genre, "
                "writing_method, status, created_at, updated_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)", row
            )
            proj_conn2.commit()
            proj_conn2.close()
    except Exception as e:
        print(f"    ✗ project_info: {e}")

    print(f"  ✓ 项目 [{project_name}] 迁移完成")


def clean_app_tables(conn: sqlite3.Connection):
    """删除应用级 DB 中的旧项目级表。"""
    print("\n清理应用级 DB 中的项目级表...")
    for table in PROJECT_TABLES:
        try:
            conn.execute(f"DROP TABLE IF EXISTS {table}")
            print(f"  ✓ 已删除: {table}")
        except Exception as e:
            print(f"  ✗ {table}: {e}")
    conn.commit()


def main():
    import argparse
    parser = argparse.ArgumentParser(description="迁移单库到双层数据库架构")
    parser.add_argument("--db", default=None,
                        help="应用级 DB 路径（默认自动检测）")
    args = parser.parse_args()

    # 确定旧库路径
    if args.db:
        db_path = Path(args.db)
    else:
        from app.config import AppConfig
        config = AppConfig()
        data_dir = Path(config.get("data_dir", Path.home() / ".novel-writer"))
        db_path = data_dir / "novel_writer.db"

    if not db_path.exists():
        print(f"✗ 未找到数据库: {db_path}")
        print("  请指定正确的路径: python scripts/migrate_to_dual_db.py --db <path>")
        sys.exit(1)

    print(f"使用数据库: {db_path}")

    # 连接旧库
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA foreign_keys=OFF")

    # 获取所有项目
    projects = conn.execute(
        "SELECT id, name, path FROM projects ORDER BY id"
    ).fetchall()

    if not projects:
        print("没有找到项目，无需迁移")
        conn.close()
        return

    print(f"找到 {len(projects)} 个项目")
    for pid, pname, ppath in projects:
        print()
        migrate_project(conn, pid, pname, ppath)

    # 清理旧的表
    clean_app_tables(conn)

    conn.execute("PRAGMA foreign_keys=ON")
    conn.close()

    print("\n=== 迁移完成 ===")
    print(f"已迁移 {len(projects)} 个项目到独立 project.db")
    print("应用级 DB 已清理（项目级表已删除）")
    print("\n建议运行迁移后测试:")
    print("  1. python app/main.py")
    print("  2. 检查项目列表是否正确显示")
    print("  3. 打开每个项目验证数据完整性")


if __name__ == "__main__":
    main()
