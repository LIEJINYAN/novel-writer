"""追踪系统 - 世界观数据接口。

将 services/world_service.py 的数据适配为追踪面板所需的按类型分组格式，
便于后续若改为 settings.py 存取时可在此处替换实现。
"""
from services.world_service import world_service


class WorldTracker:
    """世界观追踪器 - 为追踪面板提供按类型分组的世界观数据。"""

    # 设定类型（与 WorldPanel.SETTING_TYPES 保持一致）
    SETTING_TYPES = ["地点", "规则", "物品", "传说", "种族", "文化", "其他"]

    def get_tree(self, project_id: int) -> list[dict]:
        """获取按类型分组的世界观树形数据。

        返回结构：
        [
            {"category": "地点", "items": [
                {"id": 1, "name": "青云山", "type": "地点",
                 "description": "主角修炼之地", "importance": "核心"},
                ...
            ]},
            ...
        ]
        """
        all_items = world_service.list(project_id)
        return self._build_categorized_tree(all_items)

    def search(self, project_id: int, keyword: str) -> list[dict]:
        """搜索条目并返回按类型分组的结果。"""
        items = world_service.list(project_id, search=keyword)
        return self._build_categorized_tree(items)

    def filter_by_type(self, project_id: int, type_name: str) -> list[dict]:
        """按类型筛选并返回分组结果。"""
        items = world_service.list(project_id, type_filter=type_name)
        return self._build_categorized_tree(items)

    def get_item(self, setting_id: int):
        """获取单个条目。"""
        return world_service.get(setting_id)

    def delete_item(self, setting_id: int) -> bool:
        """删除条目。"""
        return world_service.delete(setting_id)

    # ---- 内部辅助 ----

    def _build_categorized_tree(self, items: list) -> list[dict]:
        """将扁平条目列表按 setting_type 分组建树。"""
        # 先按 setting_type 分组
        grouped: dict[str, list[dict]] = {}
        for item in items:
            st = item.setting_type or "其他"
            if st not in grouped:
                grouped[st] = []
            grouped[st].append({
                "id": item.id,
                "name": item.name,
                "type": st,
                "description": item.description or "",
                "importance": item.importance or "",
                "parent_id": item.parent_id,
                "children": [],
            })

        # 建立父子关系
        for cat_items in grouped.values():
            item_map = {it["id"]: it for it in cat_items}
            roots = []
            for it in cat_items:
                pid = it["parent_id"]
                if pid and pid in item_map:
                    item_map[pid]["children"].append(it)
                else:
                    roots.append(it)
            cat_items.clear()
            cat_items.extend(roots)

        # 按定义的顺序输出
        result = []
        seen = set()
        for cat in self.SETTING_TYPES:
            if cat in grouped and grouped[cat]:
                result.append({"category": cat, "items": grouped[cat]})
                seen.add(cat)
        # 未在预设类型中的补充输出
        for cat, cat_items in grouped.items():
            if cat not in seen and cat_items:
                result.append({"category": cat, "items": cat_items})

        return result


world_tracker = WorldTracker()
