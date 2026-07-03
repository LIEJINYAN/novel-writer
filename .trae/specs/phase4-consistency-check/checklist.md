# Phase 4-C：一致性检查 - 检查清单

## 规则检测引擎
- [x] Checkpoint 1.1: `run_rules` 返回 `list[CheckResult]` 结构正确
- [x] Checkpoint 1.2: 角色别名冲突检测正常触发
- [x] Checkpoint 1.3: 角色出场前置检测正常触发
- [x] Checkpoint 1.4: 时间线排序异常检测正常触发
- [x] Checkpoint 1.5: `run_ai_check` 返回 AIWorker 实例，流式输出正常

## 检查面板
- [x] Checkpoint 2.1: 侧边栏"检查"标签页存在
- [x] Checkpoint 2.2: "规则扫描"按钮执行扫描，结果按类别分组显示
- [x] Checkpoint 2.3: 结果按 severity 着色（红/黄/灰）
- [x] Checkpoint 2.4: 无 AI 配置时"AI 深度检查"按钮禁用
- [x] Checkpoint 2.5: AI 深度检查结果流式展示到"AI 分析"节点下
- [x] Checkpoint 2.6: 双击有 chapter_id 的问题跳转到对应章节
- [x] Checkpoint 2.7: 打开/关闭项目时面板自动刷新

## QSS 主题
- [x] Checkpoint 3.1: dark.qss / light.qss 包含 check_panel 样式
- [x] Checkpoint 3.2: 暗色/亮色主题下面板显示正常
