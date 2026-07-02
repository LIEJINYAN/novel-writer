# Phase 1 仓储模式实现 - 任务分解与优先级

## [x] Task 1: 创建 Repository 目录结构和 BaseRepository 基类
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 创建 `core/repositories/` 目录
  - 创建 `base.py` 文件，实现 `BaseRepository` 抽象基类
  - 实现通用 CRUD 方法：`get`, `list`, `create`, `update`, `delete`
  - 实现过滤、排序、分页查询支持
- **Acceptance Criteria Addressed**: AC-1, AC-2
- **Test Requirements**:
  - `programmatic` TR-1.1: 导入 `BaseRepository` 无错误
  - `programmatic` TR-1.2: 创建继承 `BaseRepository` 的类无错误
  - `programmatic` TR-1.3: 基类包含所有预期方法（get, list, create, update, delete）
- **Notes**: 使用 SQLAlchemy 的 session 和 query 对象实现

## [x] Task 2: 创建项目仓储 (ProjectRepository)
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 创建 `project_repository.py`
  - 实现 `ProjectRepository(BaseRepository)` 类
  - 添加项目特定的查询方法（如按名称搜索）
- **Acceptance Criteria Addressed**: AC-3
- **Test Requirements**:
  - `programmatic` TR-2.1: `ProjectRepository` 可正常导入
  - `programmatic` TR-2.2: 继承自 `BaseRepository`
  - `programmatic` TR-2.3: 可执行基本 CRUD 操作
- **Notes**: 对应 `models/project.py`

## [x] Task 3: 创建章节仓储 (ChapterRepository)
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 创建 `chapter_repository.py`
  - 实现 `ChapterRepository(BaseRepository)` 类
  - 添加按项目查询、按分卷查询等方法
- **Acceptance Criteria Addressed**: AC-3
- **Test Requirements**:
  - `programmatic` TR-3.1: `ChapterRepository` 可正常导入
  - `programmatic` TR-3.2: 支持按项目和分卷查询
- **Notes**: 对应 `models/chapter.py`

## [x] Task 4: 创建角色仓储 (CharacterRepository)
- **Priority**: medium
- **Depends On**: Task 1
- **Description**: 
  - 创建 `character_repository.py`
  - 实现 `CharacterRepository(BaseRepository)` 类
- **Acceptance Criteria Addressed**: AC-3
- **Test Requirements**:
  - `programmatic` TR-4.1: `CharacterRepository` 可正常导入
- **Notes**: 对应 `models/character.py`

## [x] Task 5: 创建情节仓储 (PlotRepository)
- **Priority**: medium
- **Depends On**: Task 1
- **Description**: 
  - 创建 `plot_repository.py`
  - 实现 `PlotArcRepository`, `PlotNodeRepository`, `PlotForeshadowRepository`
- **Acceptance Criteria Addressed**: AC-3
- **Test Requirements**:
  - `programmatic` TR-5.1: 所有情节仓储可正常导入
- **Notes**: 对应 `models/plot.py`

## [x] Task 6: 创建 AI Provider 仓储 (AIProviderRepository)
- **Priority**: medium
- **Depends On**: Task 1
- **Description**: 
  - 创建 `ai_provider_repository.py`
  - 实现 `AIProviderRepository(BaseRepository)` 类
- **Acceptance Criteria Addressed**: AC-3
- **Test Requirements**:
  - `programmatic` TR-6.1: `AIProviderRepository` 可正常导入
- **Notes**: 对应 `models/ai_provider.py`

## [x] Task 7: 创建 __init__.py 统一导出
- **Priority**: medium
- **Depends On**: Task 2-6
- **Description**: 
  - 创建 `core/repositories/__init__.py`
  - 统一导出所有仓储类
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `programmatic` TR-7.1: 可从 `core.repositories` 导入所有仓储类
- **Notes**: 使用星号导入或显式导出

## [x] Task 8: 验证所有仓储模块可正常导入
- **Priority**: high
- **Depends On**: Task 1-7
- **Description**: 
  - 运行导入测试脚本
  - 确保所有模块无语法错误
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `programmatic` TR-8.1: 所有仓储模块导入测试通过
  - `programmatic` TR-8.2: 应用启动正常，无导入错误
- **Notes**: 使用 `python -c "from core.repositories import *"` 验证
