"""仓储模式基类 - 提供通用的 CRUD 操作。"""
from __future__ import annotations
from typing import Optional, Type, TypeVar, List, Dict, Any, Tuple
from sqlalchemy import Column
from sqlalchemy.orm import Query

from models.database import db_manager

ModelType = TypeVar("ModelType")


class BaseRepository:
    """仓储模式基类 - 封装通用 CRUD 操作。"""

    def __init__(self, model: Type[ModelType]):
        self._model = model

    def get(self, entity_id: int) -> Optional[ModelType]:
        """根据 ID 获取实体。"""
        session = db_manager.get_session()
        try:
            return session.query(self._model).filter_by(id=entity_id).first()
        finally:
            session.close()

    def list(
        self,
        filters: Dict[str, Any] = None,
        order_by: Tuple[Column, str] = None,
        page: int = None,
        per_page: int = None,
    ) -> List[ModelType]:
        """列出实体，支持过滤、排序、分页。"""
        session = db_manager.get_session()
        try:
            query: Query = session.query(self._model)

            if filters:
                query = query.filter_by(**filters)

            if order_by:
                column, direction = order_by
                if direction.lower() == "desc":
                    query = query.order_by(column.desc())
                else:
                    query = query.order_by(column)

            if page is not None and per_page is not None:
                offset = (page - 1) * per_page
                query = query.offset(offset).limit(per_page)

            return query.all()
        finally:
            session.close()

    def create(self, **kwargs) -> ModelType:
        """创建新实体。"""
        session = db_manager.get_session()
        try:
            entity = self._model(**kwargs)
            session.add(entity)
            session.commit()
            session.refresh(entity)
            return entity
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def update(self, entity_id: int, **kwargs) -> Optional[ModelType]:
        """更新实体。"""
        session = db_manager.get_session()
        try:
            entity = session.query(self._model).filter_by(id=entity_id).first()
            if not entity:
                return None
            for key, value in kwargs.items():
                if hasattr(entity, key):
                    setattr(entity, key, value)
            session.commit()
            session.refresh(entity)
            return entity
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def delete(self, entity_id: int) -> bool:
        """删除实体。"""
        session = db_manager.get_session()
        try:
            entity = session.query(self._model).filter_by(id=entity_id).first()
            if not entity:
                return False
            session.delete(entity)
            session.commit()
            return True
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def count(self, filters: Dict[str, Any] = None) -> int:
        """统计实体数量。"""
        session = db_manager.get_session()
        try:
            query = session.query(self._model)
            if filters:
                query = query.filter_by(**filters)
            return query.count()
        finally:
            session.close()
