# 人工智能原理与实践 · 课程项目

本仓库收录《人工智能原理与实践》课程的实践项目代码，每个项目一个子目录，
均可离线复现：既能跑图形界面观察算法行为，也能用本地判分器逐关验收。

| 项目 | 主题 | 关键技术 | 状态 |
|---|---|---|---|
| [search-modified](search-modified/) | 搜索（基于 CS188 *Project 1: Search* 改版） | DFS / BFS / UCS / A* / 启发式设计 | ✅ 8/8 关通过 |

> 规划中：`multiagent-modified`（多智能体，Project 2 改版）等。

## 通用约定

所有项目遵循同一套结构，换项目时只需换目录：

| | |
|---|---|
| Python | **3.10**（`grading.py` 依赖 3.13 已移除的 `cgi` 模块） |
| 依赖 | 零第三方依赖，仅标准库 + `tkinter` |
| 环境 | 每个项目自带 `environment.yml`：`conda env create -f environment.yml` |
| 判分 | 进入项目目录后 `python run_autograder.py` |
| 界面 | `python pacman.py -l <layout> -p <Agent> -a fn=<搜索函数>` |

## 各项目文档

- [search-modified / README](search-modified/README.md) —— 环境搭建、架构与调用链、
  变量关系、8 关实现位置、复现与调试手册、常见错误对照
- [search-modified / 关卡说明](search-modified/关卡说明/README.md) —— 8 关原题面

## 许可与致谢

各项目源自 **UC Berkeley CS188** 的 Pacman 教学项目，原始版权声明保留在源文件头部。
本仓库定位为**个人课程学习留档**：记录自己完成作业的过程，供复盘与交流，
不提供作业代写，也不承接解题请求。若原作者或课程方认为不妥，请联系删除。
