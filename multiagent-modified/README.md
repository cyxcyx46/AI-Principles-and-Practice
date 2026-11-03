# 多智能体博弈（Multi-Agent Search）

本项目是 Educoder 课堂实训「多智能体博弈」的完整实现版本，内容为 UC Berkeley CS188
**Project 2: Multiagent search**（吃豆人对抗搜索）的改写版：题面与代码注释已中文化，判分用例为课程自建。

以吃豆人游戏为平台，从零构建能与幽灵智能博弈的 Pacman AI，核心是**博弈树搜索**的四种形态：

```
反射型评估  →  极小极大  →  α-β 剪枝  →  期望极大  →  更好的评估函数
   q1          q2          q3           q4            q5
```

**当前状态：5 关全通，判分 25/25。**

| 关 | 题目 | 分值 | 判分类 | 状态 |
|---|---|---|---|---|
| q1 | 反射Agent的评估函数 | 4 | 按表现给分 | ✅ 4/4 |
| q2 | 极小极大搜索算法 | 5 | 全过才给分 | ✅ 5/5 |
| q3 | α-β 剪枝算法 | 5 | 全过才给分 | ✅ 5/5 |
| q4 | 期望最大Agent | 5 | 全过才给分 | ✅ 5/5 |
| q5 | 更好的评估函数 | 6 | 按表现给分 | ✅ 6/6 |
| | **合计** | **25** | | **25/25** |

> 平台另有第 6 关「多智能体博弈综合」，为综合考察，不单独计分。

---

## 0. 一分钟上手

```powershell
cd multiagent-modified
conda env create -f environment.yml      # 首次
conda activate multiagent-modified

python autograder.py --no-graphics                                # ① 判分 → 25/25
python pacman.py -l minimaxClassic -p AlphaBetaAgent -a depth=2   # ② 看界面
```

看界面时 Pacman 会自己在 `minimaxClassic` 上跑一局，能直观看到它怎么躲幽灵、怎么吃豆。

---

## 1. 环境准备

### 1.1 为什么必须是 Python 3.10

`autograder.py` 第 27 行是**裸的** `import imp`，第 138 行实际调用了 `imp.load_source()`：

```python
import imp                                    # autograder.py:27

return imp.load_source(moduleName, filePath)  # autograder.py:138
```

而 `imp` 模块**在 Python 3.12 被正式移除**，所以：

```
Python 3.13 → ModuleNotFoundError: No module named 'imp'   ✗
Python 3.10 → 正常运行                                      ✓
```

仓库里若残留 `__pycache__/*.cpython-312.pyc`、`*.cpython-313.pyc`，就是这个现象留下的痕迹——
`.pyc` 在**编译阶段**就写入磁盘，随后执行 `import imp` 才失败，所以缓存留下了、程序没跑成。

### 1.2 用 conda（推荐）

```powershell
conda env create -f environment.yml
conda activate multiagent-modified
```

不想激活也可以用绝对路径 / `conda run`：

```powershell
conda run -n multiagent-modified python autograder.py -q q1 --no-graphics
D:\anaconda\envs\multiagent-modified\python.exe autograder.py -q q1 --no-graphics
```

### 1.3 依赖清单

**零第三方依赖。** 全部 import 来自标准库或项目自身模块：

| 用途 | 模块 | 来源 |
|---|---|---|
| 图形界面 | `tkinter`（Tk 8.6.13） | 标准库 |
| 判分 | `imp`（3.12 已移除）、`optparse`、`importlib` | 标准库 |
| 逻辑 | `heapq`、`random`、`math`、`pickle`、`bz2` | 标准库 |
| 可选 | `boinc` | `game.py:542` 用 `try/except` 包着，不装就没有 BOINC 进度条，不影响运行 |

`requirements.txt` 故意留空，原因写在文件内注释里。

---

## 2. 三条验证命令

三条都实测过，输出与下表一致。

### ① 判分跑通

```powershell
python autograder.py --no-graphics
```

```
Question q1: 4/4
Question q2: 5/5
Question q3: 5/5
Question q4: 5/5
Question q5: 6/6
------------------
Total: 25/25
```

> **退出码恒为 0**，即使 0 分也是 0。写脚本批量判分时不要用 `$LASTEXITCODE` / `&&` 判断成败，要解析 `Total:` 那一行。

### ② 界面跑通（弹出 tkinter 窗口）

```powershell
python pacman.py -l minimaxClassic -p AlphaBetaAgent -a depth=2
```

会弹出图形窗口，Pacman 自己跑一局。想亲手玩：

```powershell
python pacman.py -l smallClassic -p KeyboardAgent      # 方向键操控
```

### ③ 算法效果跑通（无图形，只出数据）

```powershell
python pacman.py -l minimaxClassic -p AlphaBetaAgent -a depth=2 -f -q
```

```
Scores:        516.0
Win Rate:      1/1 (1.00)
Record:        Win
```

四个智能体（`-f` 固定随机种子，结果可复现）：

| 命令 | 得分 | 结果 | 耗时 |
|---|---|---|---|
| `python pacman.py -l openClassic -k 1 -p ReflexAgent -f -q` | 1226 | Win | ~1s |
| `python pacman.py -l minimaxClassic -p MinimaxAgent -a depth=2 -f -q` | 516 | Win | 0.1s |
| `python pacman.py -l minimaxClassic -p AlphaBetaAgent -a depth=2 -f -q` | 516 | Win | 0.1s |
| `python pacman.py -l minimaxClassic -p ExpectimaxAgent -a depth=2 -f -q` | 516 | Win | 0.1s |

> minimax 与 α-β 得分**必须完全相同**——剪枝只减少搜索量，不改变决策结果。这是一条很好的自检。

---

## 3. 目录结构：每个文件负责什么

```
multiagent-modified/
├── multiAgents.py            ★ 533 行 —— 唯一需要修改的文件（5 关的全部实现）
├── autograder.py              356 行 —— 判分入口（自带 __main__ 守卫，可直接运行）
├── multiagentTestClasses.py   579 行 —— 4 个测试类（本项目的判分逻辑）
├── testClasses.py             205 行 —— Question / TestCase 基类、计分策略
├── testParser.py               87 行 —— 解析 .test / .solution 文本格式
├── grading.py                 329 行 —— Grades 累计分数、输出评分表
├── projectParams.py            19 行 —— 常量：学生代码文件 = multiAgents.py
├── submission_autograder.py    31 行 —— 平台加密判分器（末尾是 base64 密文，本地用不到）
│
├── pacman.py                  739 行 —— 游戏规则 + GameState + 命令行入口（loadAgent / runGames）
├── game.py                    779 行 —— 通用框架：Agent / Directions / Grid / AgentState / Game
├── util.py                    718 行 —— 工具：Stack / Queue / Counter / manhattanDistance / lookup
├── layout.py                  165 行 —— 解析 layouts/*.lay 地图文件
│
├── graphicsDisplay.py         739 行 —— tkinter 图形渲染
├── graphicsUtils.py           452 行 —— tkinter 绘图原语（polygon / circle / text …）
├── textDisplay.py              86 行 —— 文本渲染与 NullGraphics（--no-graphics 时用）
├── keyboardAgents.py           96 行 —— 键盘操控智能体
├── pacmanAgents.py             64 行 —— 内置智能体：LeftTurnAgent / GreedyAgent
├── ghostAgents.py              94 行 —— 幽灵策略：RandomGhost / DirectionalGhost
│
├── probe_q1.py                112 行 —— 探针：打印 q1 能拿到的全部变量真实值
├── probe_q1_rules.py          100 行 —— 探针：复现评估函数规则里的 4 个逻辑陷阱
│
├── test_cases/                        —— 88 个 .test + 87 个 .solution（q1–q5 + extra）
├── layouts/                           —— 11 张地图
├── 关卡说明/                           —— 5 关原题面（Markdown）+ 索引
├── environment.yml  requirements.txt  —— 环境定义
└── VERSION                            —— v1.004（平台版本号）
```

**除 `multiAgents.py` 外，其余文件都是平台/CS188 原始框架，不需要改。**
两个 `probe_*.py` 是调试观察工具，不参与判分，删掉也不影响运行。

### 判分只读一个文件

`projectParams.py:15` 写着：

```python
STUDENT_CODE_DEFAULT = 'multiAgents.py'
```

判分器**只加载这一个文件**。改其它文件在本地可能"看起来生效"，但换环境就不成立。

---

## 4. 架构：一次决策经过了谁

### 4.1 交互式运行（图形界面）

```
pacman.py
 └─ readCommand(argv)                 解析命令行
 └─ loadAgent('AlphaBetaAgent', …)    反射导入 multiAgents 里的类
 └─ runGames(layout, pacman, ghosts)  建 GameState，进主循环
     └─ game.py: Game.run()
         └─ agent.getAction(observation)      ★ 你的代码在这里被调用
             └─ 返回 Directions.NORTH / SOUTH / EAST / WEST / STOP
         └─ PacmanRules.applyAction / GhostRules.applyAction
         └─ display.update(state)            图形或文本渲染
```

### 4.2 判分

```
autograder.py
 └─ loadModuleFile('multiAgents.py')           动态导入学生代码
 └─ loadModuleFile('multiagentTestClasses.py') 导入测试类
 └─ evaluate()  按 test_cases/CONFIG 的 order: "q1 q2 q3 q4 q5" 逐关跑
     └─ 逐个 .test 文件 → TestParser 解析成 dict
     └─ 按 dict['class'] 实例化测试类：
          PacmanGameTreeTest   — 真的跑对局，看胜率 / 平均分（q1 的 grade-agent、q2~q4 的 *pacman-game）
          GraphGameTreeTest    — 给定博弈树，直接比对展开值与访问节点（q2~q4 的 *tree 类）
          EvalAgentTest        — 单独测评估函数（q1）
     └─ grading.Grades 累计 → 打印 Provisional grades 表
```

本项目 `autograder.py` **自带** `if __name__ == '__main__':`（第 334 行），所以直接
`python autograder.py` 就能跑，不需要额外补入口文件。

### 4.3 唯一的契约：`Agent.getAction`

```python
# game.py:34
class Agent:
    def getAction(self, state):
        raiseNotDefined()
```

框架只要求这一个方法。`game.py: Game.run()` 里的调用是：

```python
action = timed_func(observation)      # game.py:694，observation 就是 GameState
```

所以你的智能体收到的是**完整游戏状态**，返回一个动作字符串。

---

## 5. 变量与对象关系（重点）

### 5.1 三个核心对象

| 类 | 定义位置 | 是什么 | 方法数 |
|---|---|---|---|
| `GameState` | `pacman.py:61` | **局面**。所有查询都从这里出发 | 27 |
| `AgentState` | `game.py:127` | 单个**智能体**的位置/朝向。幽灵就是带 `scaredTimer` 的 AgentState | 7 |
| `Grid` | `game.py:172` | 二维网格。**食物、墙都是 Grid** | 15 |

`GameState` 最常用的 10 个方法（`probe_q1.py` 全部实测过）：

| 方法 | 返回 | 实测样例 |
|---|---|---|
| `getPacmanPosition()` | `(x, y)` 元组 | `(4, 7)` |
| `getFood()` | `Grid`（**不是 list**） | 25 × 9 的网格 |
| `getGhostStates()` | `[AgentState]` | 幽灵列表 |
| `getCapsules()` | `[(x, y)]` | `[(23, 1)]` |
| `getScore()` | `float` | `0.0` |
| `getNumFood()` | `int` | `86` |
| `getLegalActions(agentIndex=0)` | `[str]` | `['West', 'Stop', 'East', 'South']` |
| `generatePacmanSuccessor(action)` | 新 `GameState` | 走完这一步的局面 |
| `generateSuccessor(agentIndex, action)` | 新 `GameState` | 任意智能体走完的局面（q2~q4 用这个） |
| `isWin()` / `isLose()` | `bool` | 终局判断 |

**三个必须记住的坑：**

1. **`getFood()` 返回 `Grid`，不是 list**。要 `.asList()` 才是 `[(x, y), …]`。
   ```python
   food = state.getFood()
   food.width, food.height        # 25, 9
   food.asList()                  # [(1, 1), (1, 2), …]
   food[1][1]                     # True / False   ← 索引是 [x][y]，不是 [y][x]
   ```
2. **`getLegalActions()` 里包含 `'Stop'`**。搜索时通常要显式剔掉，否则智能体会站着不动。
3. **`AgentState` 没有单独的 GhostState 类**。幽灵就是 `AgentState` 实例，额外带一个 `scaredTimer` 字段：
   `> 0` 表示受惊（此时能被吃），`== 0` 表示危险。

### 5.2 七个高频名字

| 名字 | 类型 | 从哪来 | 干什么用 |
|---|---|---|---|
| `gameState` | `GameState` | 框架传入 | 当前局面，只读 |
| `agentIndex` | `int` | 约定 | **0 = Pacman**，幽灵为 1…N-1 |
| `action` | `str` | `getLegalActions()` | `'North'` / `'South'` / `'East'` / `'West'` / `'Stop'` |
| `successorState` | `GameState` | `generateSuccessor()` | 模拟走一步后的局面 |
| `depth` | `int` | `MultiAgentSearchAgent.__init__` | 搜索深度，`-a depth=3` 可传 |
| `evaluationFunction` | `function` | `util.lookup(evalFn, globals())` | 局面打分，`-a evalFn=better` 可传 |
| `manhattanDistance` | `function` | `util.py:236` | 最常用的距离度量 |

`util.lookup(module, glob, field)` 是个小心机：它按**名字字符串**在模块全局里找对象，
所以 `-a evalFn=betterEvaluationFunction` 能把函数名当成参数传进来。`multiAgents.py:533`
的 `better = betterEvaluationFunction` 就是给这种用法准备的短别名。

### 5.3 分数构成（从 `pacman.py` 源码实测）

| 事件 | 分值 | 源码位置 |
|---|---|---|
| 吃一颗豆 | **+10** | `pacman.py:380` |
| 吃能量豆 | **+500** | `pacman.py:387` |
| 吃受惊幽灵 | **+200** | `pacman.py:460` |
| 每走一步 | **−1** | `pacman.py:122`（`TIME_PENALTY = 1`） |
| 被未受惊幽灵碰到 | **−500 且立刻判负** | `pacman.py:467` |

碰撞阈值 `COLLISION_TOLERANCE = 0.7`（`pacman.py:272`）：**曼哈顿距离 ≤ 0.7 即死亡**，
也就是"贴身"。所以评估函数里对幽灵距离 ≤ 1 的处理，本质是在估"下一帧会不会死"。

### 5.4 一次极小极大决策的数据流

以 `depth=2`、1 只幽灵为例：

```
getAction(gameState)                        depth=0
 └─ 遍历 Pacman 合法动作（已剔除 Stop）
     └─ minVal(successor, depth=0, index=1)        幽灵回合
         └─ 遍历幽灵合法动作
             └─ 是最后一个幽灵 → maxVal(successor, depth=0)   ← 深度在这里 +1
                 └─ depth 变成 1，== self.depth → 到叶，返回 evaluationFunction(state)
         └─ 取 min
 └─ 取 max → 返回最佳动作
```

**关键点：深度不是在 `getAction` 里减，而是在 `maxVal` 开头 `depth += 1`。**
因为一个"完整层"= Pacman 走一步 + **所有**幽灵各走一步，只有回到 Pacman 回合才算降一层。
把 `depth += 1` 写到幽灵层会导致层数算错、搜索过浅或过深。

---

## 6. 五关一览：实现位置

### 6.1 平台给定 vs 自己编写

`multiAgents.py` 里**平台已给定、不要改**的部分：

| 位置 | 内容 | 作用 |
|---|---|---|
| `L14–30` | `ReflexAgent.getAction` | 反射型智能体的决策循环：对每个动作调 `evaluationFunction` 取最大，并列时随机选 |
| `L131–138` | `scoreEvaluationFunction` | 默认评估函数，只返回 `getScore()` |
| `L152–155` | `MultiAgentSearchAgent.__init__` | 解析 `evalFn` / `depth` 两个命令行参数 |
| `L533` | `better = betterEvaluationFunction` | 给 `-a evalFn=better` 用的短别名 |

**自己编写**的部分（全部在 `BEGIN` / `END` 标记之间）：

| 关 | 题目 | 函数 | 行号 | 说明 |
|---|---|---|---|---|
| 1 | 反射Agent的评估函数 | `ReflexAgent.evaluationFunction` | **L52–128** | 终局优先 + 食物吸引 + 幽灵攻防 |
| 2 | 极小极大搜索算法 | `MinimaxAgent.getAction` + `maxVal` + `minVal` | **L184–260** | Pacman 层取 max，幽灵层取 min |
| 3 | α-β 剪枝算法 | `AlphaBetaAgent.getAction` + `maxVal` + `minVal` | **L272–375** | 在 q2 上加 α/β 窗口 |
| 4 | 期望最大Agent | `ExpectimaxAgent.getAction` + `maxiExp` + `miniExp` | **L389–467** | 幽灵层改为按动作数取期望 |
| 5 | 更好的评估函数 | `betterEvaluationFunction` | **L474–529** | 多特征线性组合 |

> 用 `Select-String -Path multiAgents.py -Pattern 'BEGIN'` 可随时定位这 5 个起点（行号会随编辑变化）。

### 6.2 计分方式

各关 `test_cases/qN/CONFIG` 定义了判分策略，两类含义不同：

| 判分类 | 用于 | 含义 |
|---|---|---|
| `PassAllTestsQuestion` | q2 / q3 / q4 | **所有用例全过才给分**，一个不过整关 0 分 |
| `PartialCreditQuestion` | q1 / q5 | **按表现分档给分**（平均分 / 胜率门槛） |

q1 的门槛（`test_cases/q1/grade-agent.test`）：

```
layoutName: "openClassic"     地图
numGames: "10"                打 10 局
ghosts: "[RandomGhost(1)]"    1 只随机幽灵
scoreThresholds: "500 1000"   平均分 ≥500 得 1 分，≥1000 得 2 分
winsThresholds: "5 10"        胜 ≥5 局得 1 分，胜 10 局得 2 分
```

q2 / q3 / q4 各有 34 / 34 / 17 条用例，从"两三层的小博弈树"到"真实对局"逐级加压。

---

## 7. 逐关说明（设计要点与坑）

### q1 反射Agent的评估函数

`evaluationFunction(currentGameState, action)` 收的是**当前局面 + 一个候选动作**，
不是后继状态。所以第一步必须自己做转换：

```python
successorGameState = currentGameState.generatePacmanSuccessor(action)
```

设计分五层：终局 → 基础分 → 食物吸引 → 幽灵攻防 → 原地惩罚。

踩过并验证过的四个逻辑坑（`probe_q1_rules.py` 可复现）：

| 坑 | 现象 | 处理 |
|---|---|---|
| **乘法惩罚在负分时反向** | `-100 * 0.01 = -1`，反而比安全的 `-50` 更"好"，智能体主动扑向幽灵 | 先平移 `+1000` 再乘、再移回，保证变换单调 |
| `0 < scaredTimer < 39` **漏判** | 刚吃能量豆那一步 `scaredTimer = 40`，被判成"不受惊"，该追时掉头跑 | 放宽为 `> 0` |
| `newPos in foodlist` **恒为假** | 吃掉的那颗豆已从后继 `newFood` 移除，判断永远不成立 | 改用 `successorGameState.getNumFood() < currentGameState.getNumFood()` |
| **缺终局判定 / 与 Stop 撞值** | 输局和"不动"都给 −999，无法区分 | 终局用 `±999999`，与 Stop 的 −999 拉开量级 |

### q2 极小极大搜索算法

`depth` 只在 `maxVal` 开头 `+= 1`，幽灵层之间保持同一深度（原因见 5.4）。
三个终局出口都要判：`depth == self.depth`、`isWin()`、`isLose()`。
`getAction` 里显式剔除 `Directions.STOP`。

### q3 α-β 剪枝算法

在 q2 结构上多加两个参数，剪枝规则：

- **Max 层**：`value > beta` 时直接返回（β 剪枝），之后 `alpha = max(alpha, value)`
- **Min 层**：`value < alpha` 时直接返回（α 剪枝），之后 `beta = min(beta, value)`

**验收标准不是"能跑"，而是"结果必须与 q2 完全一致"** —— q3 与 q2 用的是同一批 34 个用例名，
剪枝只应减少访问节点，不应改变选择。实测 `minimaxClassic` 上两者得分都是 516，正是这个道理。

### q4 期望最大Agent

关键差异在幽灵层：**不取 min，取按动作数平均的期望值**。

```python
v += m / numActions      # m 是某个幽灵动作下的后续值
```

q4 的深度计数方向与 q2/q3 相反（`maxiExp` 收到的是**剩余深度**，幽灵层走完才 `depth - 1`），
两种写法都正确，但**同一份代码里不要混用**，否则层数会少算或多算一层。

### q5 更好的评估函数

注意签名与 q1 不同：**没有 `self`，只有一个参数**。

```python
def betterEvaluationFunction(currentGameState):     # L470
```

它用于 q2/q3/q4 的搜索智能体，可以这样指定：

```powershell
python pacman.py -l minimaxClassic -p MinimaxAgent -a depth=2,evalFn=better
```

设计上把局面拆成几组特征加权求和：基础分、最近食物距离（倒数）、剩余食物数（负权重）、
幽灵（受惊则靠近给奖励、危险则靠近给重罚）、能量豆距离。

> 一个可观察的行为：受惊幽灵的"猎捕奖励"和"避险惩罚"是两个独立的 `if`，
> 所以受惊幽灵贴身时两条都会生效，净收益可能是负的。调参时可以留意这一点。

---

## 8. 复现与调试手册

### 8.1 判分

```powershell
python autograder.py --no-graphics                                  # 全部 5 关
python autograder.py -q q2 --no-graphics                            # 只判某一关
python autograder.py -t test_cases/q2/0-small-tree --no-graphics    # 只跑一条用例
```

**两个必须避开的参数坑：**

| 写法 | 结果 |
|---|---|
| `-q 1` | ✗ `FileNotFoundError: test_cases\1\CONFIG` —— 必须 `-q q1`，带 `q` 前缀 |
| `-t q2/0-small-tree` | ✗ `FileNotFoundError: 'q2/0-small-tree.test'` —— 必须带 `test_cases/` |

### 8.2 图形界面

```powershell
python pacman.py -l smallClassic -p KeyboardAgent                    # 键盘操控
python pacman.py -l minimaxClassic -p AlphaBetaAgent -a depth=2      # 看 AI 自己跑
python pacman.py -l smallClassic -p ReflexAgent -t                   # 文本界面（无窗口）
python pacman.py -l smallClassic -p ReflexAgent -q                   # 完全不显示
```

| 参数 | 作用 |
|---|---|
| `-l` | 地图名（`layouts/` 下的文件名，不带 `.lay`） |
| `-p` | 智能体类名（`multiAgents.py` 里的类，或内置 `GreedyAgent` / `KeyboardAgent`） |
| `-a` | 传给智能体的参数：`depth=2`、`evalFn=better`、`depth=3,evalFn=better` |
| `-g` | 幽灵类型：`RandomGhost`（默认）/ `DirectionalGhost` |
| `-k` | 幽灵数量 |
| `-n` | 连打几局，看平均分与胜率 |
| `-f` | 固定随机种子，**结果可复现**（对比算法时必加） |
| `-t` / `-q` | 文本界面 / 无输出 |
| `--frameTime 0` | 全速播放 |
| `-c` | 捕获智能体异常，不中断整个对局 |
| `--timeout` | 单次决策超时秒数（默认 30），防死循环 |

可用地图 11 张：

```
capsuleClassic  contestClassic  mediumClassic  minimaxClassic  openClassic
originalClassic powerClassic    smallClassic   testClassic     trappedClassic  trickyClassic
```

> **注意**：`openClassic` + `depth=3` 会非常慢（地图大、分支多），演示深度学习请用
> `minimaxClassic`（小图，`depth=2` 约 0.1 秒一局）。

### 8.3 探针脚本（本项目独有的观察工具）

```powershell
python probe_q1.py          # 打印 GameState 全部 getter 的真实值 + 逐动作评分分解
python probe_q1_rules.py    # 复现评估函数规则里的 4 个逻辑陷阱（负分乘法反向等）
```

`probe_q1.py` 的输出节选：

```
① Agent 直接拿到的是 GameState 对象
getPacmanPosition()     : (4, 7)  <- 元组 (x, y)
getNumFood()            : 86
② 食物：getFood() 返回的是 Grid 二维网格，不是 list
尺寸 width x height     : 25 x 9  <- 注意 Grid 是 [x][y]
③ 幽灵：getGhostStates() 返回 AgentState 列表
      scaredTimer       : 0 （>0 表示处于受惊状态，可被吃）
④ 接口链路：getAction -> generatePacmanSuccessor -> evaluationFunction
  动作            后继位置        剩余豆子   分数    evaluationFunction
  West         (3, 7)         86         -1.0    4.000
```

改 q2~q5 时照着改这个脚本，就能看到搜索层拿到的状态是什么。

### 8.4 常见错误对照

| 现象 | 原因 | 处理 |
|---|---|---|
| `ModuleNotFoundError: No module named 'imp'` | 用了 Python 3.12+ | 换 3.10 环境 |
| `TypeError: '>' not supported between NoneType and NoneType` | 评估函数忘了 `return`，返回 `None` | 检查函数末尾 |
| 得分全 0，10 局全负 | 同上（`max(None, None)` 崩溃后对局判负） | 同上 |
| `Student move: None` / `Optimal move: pacLeft` | `getAction` 返回了 `None` 或非法动作 | 检查所有 return 分支 |
| 智能体原地不动 | 没剔除 `Directions.STOP`，或给 Stop 的分数不够低 | 搜索时 `legalActions.remove(Directions.STOP)` |
| `-q 1` 报 `FileNotFoundError` | 参数少了 `q` 前缀 | 用 `-q q1` |
| `-t` 报 `FileNotFoundError` | 路径不完整 | 用 `-t test_cases/q2/xxx` |
| α-β 结果与 minimax 不一致 | 剪枝条件写错（`>` 与 `>=` 混用，或更新 α/β 的时机错） | 先用 `-q q2` 拿到标准答案再对照 |
| 搜索层次比预期浅/深一层 | `depth += 1` 写在了幽灵层 | 只在 Pacman 层递增 |
| 深度稍大就卡死 | 地图大 + 分支多 | 换小图或降 `depth`，调 `--timeout` |

---

## 9. 注意事项

1. **不要跑 `--generate-solutions`**。它会用你当前的代码重新生成 `test_cases/**/*.solution`，
   把官方标准答案覆盖掉，之后这批用例就不能用来判分了。

2. **不要改方法签名**。`getAction(self, gameState)`、`evaluationFunction(self, currentGameState, action)`、
   `betterEvaluationFunction(currentGameState)` 的头部是框架调用入口，只改 `BEGIN` / `END` 之间的内容。

3. **只改 `multiAgents.py`**。判分器只加载这一个文件（`projectParams.py:15`）。

4. **`submission_autograder.py` 用不到**。它是平台加密过的判分器（末尾是 base64 密文），
   本地判分走 `autograder.py`。保留它只为和平台文件结构对齐。

5. **`test_cases/extra/` 不计分**。它不在 `test_cases/CONFIG` 的 `order: "q1 q2 q3 q4 q5"` 里，
   而且没有 `.solution` 文件，所以总数是 88 个 `.test` / 87 个 `.solution`。

---

## 10. 来源与许可

本项目源自 **UC Berkeley CS188** 的 *Project 2: Multiagent search*，经 Educoder 平台改写
（题面中文化、判分用例自建）。各源文件头部的原始版权声明已完整保留。

> 原始声明节选：*"You are free to use or extend these projects for educational purposes
> provided that (1) you do not distribute or publish solutions, (2) you retain this notice,
> and (3) you provide clear attribution to UC Berkeley, including a link to http://ai.berkeley.edu."*

本仓库定位为**个人课程学习留档**：记录自己完成课程作业后的代码，用于复盘与交流，
不提供作业代写，也不承接解题请求。若原作者或课程方认为不妥，请联系删除，会立即下架。
