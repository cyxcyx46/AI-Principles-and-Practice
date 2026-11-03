# 第 1 关：反射Agent的评估函数

| 项目 | 值 |
|---|---|
| 关卡标识 | `nvbx25leh9cs` |
| challenge_id | 5809906 |
| 所属实训 | 多智能体博弈（id 2193188，共 6 关） |
| 分值 | 100 |
| 限时 | 30 分钟 |
| 运行镜像 | ["VSCode1.105/VNC"] |

## 涉及文件

- `multiagent-modified/multiAgents.py`
- `multiagent-modified/pacman.py`
- `multiagent-modified/game.py`
- `multiagent-modified/util.py`

## 判分用例

```
### Question q1: 4/4 ###


Provisional grades
==================
Question q1: 4/4
------------------
Total: 4/4
```

## 题目正文

---

[TOC]

---

### 任务描述

本关任务：在 `multiAgents.py` 中设计一个评估函数，用于驱动一个反射型智能体（`ReflexAgent`）在 `Pacman` 游戏中做出明智的决策。

### 相关知识

为了完成本关任务，你需要掌握：1.环境特征提取与状态表示；2.反射型智能体的决策机制；3.评估函数的设计范式与数学模型。


#### 环境特征提取与状态表示

在多智能体对抗游戏` Pacman` 中，智能体需要尽可能多地捕食食物，同时规避幽灵的追击。由于游戏状态呈现动态变化，构建优秀评估函数的前提是对当前环境进行有效的特征提取（`Feature Extraction`）。常见的关键特征包括“智能体至最近食物的距离”、“周边特定范围内的幽灵数量”等。

<center>
  <img width="70%" src="/api/attachments/att-19c7b3c6479e61920?type=image/png" alt="Pacman Game Screenshot" />
</center>

`Pacman` 的游戏状态（`GameState`）封装了当前网格世界的所有环境参数。在代码实现中，系统通过 `generatePacmanSuccessor(action)` 方法模拟出执行特定动作后的后继状态（`Successor State`）。开发者需从该后继状态中提取以下核心特征变量以供评估使用：

- `newPos`: 模拟执行动作后，Pacman 的预测坐标` (x, y)`。
- `newFood`: 执行动作后，剩余食物的网格分布。调用 `.asList() `可转换为坐标列表。
- `newGhostStates`: 执行动作后的所有幽灵状态对象。
- `newScaredTimes`: 一个数字列表，表示每个幽灵受惊状态（变成可被吃掉的蓝色状态）剩余的步数。
- `manhattanDistance`: 辅助函数，用于计算两点间的曼哈顿距离（网格距离）。

#### 反射型智能体的决策机制

反射型智能体（`Reflex Agent`）属于一种基于单步前瞻的反应式智能体。该智能体不构建复杂的深度搜索树或进行长远的战略规划，而是仅关注“执行某一候选动作后，紧随其后的局部状态的优劣”

本实验中 `ReflexAgent` 的决策执行流可归纳为以下三个核心步骤：首先，系统遍历当前状态下所有合法的候选动作（如向上、向下等），并对应生成所有的后继游戏状态；其次，将上述后继状态逐一输入至开发者设计完成的评估函数中，计算得出该状态的具体量化评分；最后，智能体将选取评分最高的动作予以真实执行。若存在多个同等最高分的动作，则触发随机选择策略。

<center>
  <img width="50%" src="/api/attachments/att-19c7b4dfa4184843a?type=image/png" alt="Reflex Agent Logic" />
</center>

#### 评估函数的设计范式与数学模型

评估函数的输入为某一确定的游戏状态，输出为量化的浮点数值。该数值客观反映了当前状态对 `Pacman` 的有利程度，数值愈高代表状态愈优。本实验的评估逻辑采用基于曼哈顿距离的乘法评分模型，并严格根据“幽灵是否处于受惊状态”进行精细化的状态分治与策略切换。其核心决策与计算流程可划分为以下三个阶段：

**第一阶段**：预判拦截与基础分计算。系统首先需对致命动作进行拦截。若候选动作为原地停止（`Stop`），在面临幽灵追击时此动作极易导致智能体受困或死亡，因此需直接赋予极低的惩罚得分（例如 `-999`）。在排除致命动作后，无论系统处于何种博弈模式，状态评估的基准均建立在“趋向食物”这一根本目标上。基础得分的数学计算公式设定为：$$ \text{Base} = \frac{1}{d_{food-min}^4} $$ ，其中，$$d_{food-min}$$ 表示智能体至最近食物的网格距离。
   
**第二阶段**：基于受惊时间的状态分治。系统需遍历所有幽灵的受惊倒计时 `newScaredTimes`，进而判断当前所处的博弈模式。若不存在受惊时间位于 (0, 39) 区间的幽灵，系统判定为普通/危险模式。此时的核心策略以安全避险与吞食普通豆为主。系统需进一步检查最近幽灵距离是否小于安全阈值（本实验设定$$d = 5$$）。若距离处于安全范围，则状态得分为基础分与游戏系统基底得分之和，即$$V = \text{Base} + \text{GameScore}$$；若幽灵已逼近危险阈值，则必须对进入范围的所有幽灵进行分级惩罚：当处于极度危险区（$$dist < 6$$）时，得分为$$ V = V \cdot dist^4 $$；当处于警戒区（$$6 < dist < 10$$）时，得分为$$ V = V \cdot dist $$。

反之，若存在至少一个幽灵处于受惊状态（$$0 < t < 39$$），系统则切换至进攻模式。此时策略演变为“追捕受惊幽灵”与“躲避未受惊幽灵”的并发执行。系统需将幽灵划分为可追击幽灵（$$t < 40$$）与仍具威胁幽灵（$$t \ge 40$$），并采用混合加权公式进行计算：$$ V = \text{Base} \cdot \left( \prod_{i \in Scared} \frac{1}{dist_i^2} \right) \cdot \left( \prod_{j \in UnScared} dist_j^4 \right) + \text{GameScore} $$，该公式旨在通过距离平方的倒数奖励进攻行为，同时利用距离的四次方惩罚靠近危险幽灵的行为。


**第三阶段**：位置特征修正。 在完成上述阶段性评估后，系统将进行最终的位置修正检验。若预测的新位置 `newPos` 恰好与当前食物列表中的某一坐标重合（即该步动作可确切吞食一颗食物），则在最终得分的基础上施加1.1倍的乘数奖励，以进一步强化觅食倾向。



### 编程要求

根据提示，在 `multiAgents.py` 右侧编辑器 `BEGIN-END` 之间补充代码。你需要按照以下步骤实现逻辑：

1.  特殊动作拦截：如果 `action` 为 `'Stop'`，直接返回 `-999`。
2.  数据准备：
    *   将 `newFood` 转为列表。
    *   计算并排序 `FoodDistance`。
    *   计算 `GhostDistance`。
3.  模式判定：
    *   遍历 `newScaredTimes`。如果存在时间 $$0 < t < 39$$ ，将标志位 `IsScared` 设为 `True` 并跳出循环。
    
    
4.  分支计算：
    *   保证有食物且最小食物距离 $$>0$$ 时，计算基础分 `s = 1 / (FoodDistance[0] ** 4)`。
    *   如果 `IsScared` 为 `False`：
        *   判断排序后的最近幽灵距离是否 `< d` (设 $$d=5$$)。如果是，按公式进行分级乘法惩罚。
        *   如果安全，`s = successorGameState.getScore() + s`。
    *   如果 `IsScared` 为 `True`：
        *   使用列表推导式分类 `ScaredGhost` 和 `UnScaredGhost` 的索引。
        *   计算奖励与惩罚 `successorGameState.getScore()`。

     
5.  统一返回：检查位置修正（`if newPos in foodlist: s = s * 1.1`），最终返回评估值 `s` (或 `a`)。



### 测试说明

平台会对你编写的代码进行测试。

**预期输出**：

```
Question q1
===========

Pacman emerges victorious! Score: 1215
Pacman emerges victorious! Score: 1241
Pacman emerges victorious! Score: 1397
Pacman emerges victorious! Score: 1236
Pacman emerges victorious! Score: 1237
Pacman emerges victorious! Score: 1077
Pacman emerges victorious! Score: 1243
Pacman emerges victorious! Score: 1228
Pacman emerges victorious! Score: 1231
Pacman emerges victorious! Score: 1225
Average Score: 1233.0
Scores:        1215.0, 1241.0, 1397.0, 1236.0, 1237.0, 1077.0, 1243.0, 1228.0, 1231.0, 1225.0
Win Rate:      10/10 (1.00)
Record:        Win, Win, Win, Win, Win, Win, Win, Win, Win, Win


### Question q1: 4/4 ###


Provisional grades
==================
Question q1: 4/4
------------------
Total: 4/4 
```


---
开始你的任务吧，祝你成功！
