# 路径搜索（Path Search）

> **人工智能原理与实践 · 项目一**
> 基于 [UC Berkeley CS188 *Project 1: Search*](http://ai.berkeley.edu/search.html) 的教学改版，
> 8 个关卡覆盖图搜索、启发式设计与次优搜索。

本项目**完整可离线运行**：既有图形界面可以看 Pacman 跑，也有本地判分器可以逐关验收，
不依赖任何在线平台。

| | |
|---|---|
| 关卡数 | 8（q1 ~ q8） |
| 满分 | 25 分（q7 为 4 分，其余各 3 分） |
| 第三方依赖 | **无**（仅 Python 标准库 + tkinter） |
| Python | **3.10** |
| 体积 | 约 525 KB（含全部测试数据） |

---

## 0. 一分钟上手

```bash
cd search-modified
conda env create -f environment.yml     # Python 3.10
conda activate search-modified

python run_autograder.py                                    # 判全部 8 关
python pacman.py -l mediumMaze -p SearchAgent -a fn=dfs     # 跑图形界面
```

预期判分输出：

```
Question q1: 3/3
Question q2: 3/3
Question q3: 3/3
Question q4: 3/3
Question q5: 3/3
Question q6: 3/3
Question q7: 5/4
Question q8: 3/3
------------------
Total: 26/25
```

> `q7 5/4` 不是错误：该关满分 4 分，计分方式是 `basePoints(1) + 跨过门槛数(4)`，
> 本地判分器不做封顶，所以显示 5 分、总分 26。平台侧通常封顶为 4 分 / 总 25 分。

---

## 1. 环境准备

### 1.1 为什么必须是 Python 3.10

`grading.py` 使用了 `import cgi`，而 `cgi` 模块在 **Python 3.13 已被移除**。
用 3.13 会直接：

```
ModuleNotFoundError: No module named 'cgi'
```

### 1.2 用 conda（推荐）

```bash
conda env create -f environment.yml
conda activate search-modified
```

### 1.3 依赖清单

**本项目零第三方依赖**，`requirements.txt` 是空的，这是正确的：

| 用途 | 模块 | 来源 |
|---|---|---|
| 图形界面 | `tkinter`（Tk 8.6） | 标准库（随 CPython/Anaconda 安装） |
| 判分 | `cgi` | 标准库（3.10） |
| 搜索 / 容器 | `heapq`、`collections` | 标准库 |
| 可选 | `boinc` | `game.py` 用 `try/except` 包着，不装就不启用 BOINC 进度条 |

---

## 2. 三条验证命令

跑完这三条，说明环境完全正常。

```bash
# ① 判分跑通
python run_autograder.py

# ② 界面跑通（弹出 tkinter 窗口，Pacman 会动）
python pacman.py -l mediumMaze -p SearchAgent -a fn=dfs

# ③ 纯算法跑通（八数码：BFS / A*(h1) / A*(h2) 对比）
python eightpuzzle.py
```

没有图形环境（远程服务器 / WSL）时，把界面换成文本模式：

```bash
python pacman.py -l mediumMaze -p SearchAgent -a fn=dfs -t --frameTime 0.05
```

---

## 3. 目录结构：每个文件负责什么

```
search-modified/
├── search.py                 ★ 你实现 4 个搜索算法的地方
├── searchAgents.py           ★ 你实现 4 个启发式 / 状态空间的地方
├── run_autograder.py         本地判分入口（补上 autograder.py 缺失的 __main__）
│
├── autograder.py             判分主程序：解析参数、装载模块、跑用例、汇总分数
├── grading.py                分数对象 Grades：加分、封顶、输出报告
├── testClasses.py            题目基类 Question 与 TestCase（PassAllTests / PartialCredit 等）
├── testParser.py             把 .test 文本解析成测试定义
├── searchTestClasses.py      具体测试类：GraphSearchTest / PacmanSearchTest /
│                             CornerProblemTest / HeuristicTest / HeuristicGrade / ClosestDotTest
├── submission_autograder.py  平台侧加密判分脚本（本地用不到，保留以对齐平台文件）
│
├── pacman.py                 游戏主程序：GameState、命令行参数、runGames、loadAgent
├── game.py                   游戏引擎：Agent / Game / Directions / Actions / Grid / GameStateData
├── layout.py                 解析 layouts/*.lay 地图
├── util.py                   数据结构与工具：Stack / Queue / PriorityQueue / Counter /
│                             raiseNotDefined / TimeoutFunction
├── projectParams.py          项目配置：学生代码文件名、测试类文件名、项目名
│
├── textDisplay.py            文本显示（-t）
├── graphicsDisplay.py        tkinter 图形显示（默认）
├── graphicsUtils.py          tkinter 绘图原语（圆、线、文字、事件）
├── keyboardAgents.py         人类玩家 KeyboardAgent（方向键）
├── pacmanAgents.py           现成 Agent：LeftTurnAgent、GreedyAgent
├── ghostAgents.py            幽灵 AI：RandomGhost、DirectionalGhost
├── eightpuzzle.py            八数码滑块的独立 demo（q2/q4 的纯算法验证场）
│
├── layouts/                  38 个地图 .lay
├── test_cases/               8 个关卡目录 + 根 CONFIG
│   ├── CONFIG                总配置
│   └── q1 … q8/              每关：CONFIG + *.test + *.solution
├── 关卡说明/                  8 关题面 Markdown + 索引
├── environment.yml           conda 环境定义
└── requirements.txt          空（无第三方依赖）
```

**★ 标记的两个文件是唯一需要动手写的**，其余全部是教学框架，不要修改。

---

## 4. 架构：一次搜索经过了谁

### 4.1 交互式运行（图形界面）

```
python pacman.py -l mediumMaze -p SearchAgent -a fn=dfs
        │
        ├─ pacman.readCommand()          解析 -l / -p / -a 参数
        ├─ pacman.loadAgent()            按 -p 实例化 SearchAgent
        │      └─ searchAgents.SearchAgent.__init__
        │             ├─ fn=dfs  → getattr(search, 'dfs') → search.depthFirstSearch
        │             └─ prob=PositionSearchProblem → searchAgents.PositionSearchProblem
        │
        └─ pacman.runGames()
               ├─ layout.getLayout('mediumMaze')      解析地图
               ├─ GameState.initialize(layout, 0)     构造初始局面
               └─ Game.run()                          主循环
                      ├─ agent.registerInitialState(state)
                      │      └─ 你的 depthFirstSearch(problem) 被调用一次
                      │             返回 actions 列表
                      └─ 每帧 agent.getAction(state)
                             └─ 从 actions 里按下标取出下一个动作
```

关键：**搜索只跑一次**，一次性算出整条动作序列，之后每帧只是"播放"。

### 4.2 判分

```
run_autograder.py
 └─ autograder.main()
     ├─ readCommand()                      解析 -q / -t / -p 等
     ├─ loadModuleFile('search' / 'searchAgents')
     ├─ getTestSubdirs()                   处理 depends（q5→q2，q6/q7→q4）
     └─ evaluate()
         ├─ testParser.TestParser('q1/CONFIG').parse()      读题
         ├─ … 对每个 *.test 构造 TestCase
         └─ Question.execute()
             └─ TestCase.execute(grades, moduleDict, solutionDict)
                 └─ searchTestClasses.GraphSearchTest.execute()
                     ├─ problem = GraphSearch(图文本)      ★ 造题
                     └─ search.depthFirstSearch(problem)   ★ 调你的函数
                         └─ 与 .solution 比对 → grades.addPoints()
```

**同一个 `depthFirstSearch`，判分时拿到的是 `GraphSearch`，图形界面时拿到的是
`PositionSearchProblem`** —— 这就是为什么必须只依赖接口、不假设具体类型。

### 4.3 唯一的契约：`SearchProblem` 的 4 个方法

`search.py:10` 定义了抽象基类 `SearchProblem`，任何搜索问题都必须提供：

| 方法 | 返回 | 你的代码怎么用 |
|---|---|---|
| `getStartState()` | 一个 `state` | 压栈 / 入队的起点 |
| `isGoalState(state)` | `True/False` | 判断是否结束 |
| `getSuccessors(state)` | `[(后继state, action, stepCost), …]` | 展开当前节点 |
| `getCostOfActions(actions)` | 数值 | 计算动作序列总代价（本题一般用不到） |

`search.py:188` 的 `nullHeuristic` 是默认启发式（恒返回 0）；
`util.py:448` 的 `util.raiseNotDefined()` 是占位函数——模板里没写的地方调它会抛异常。

---

## 5. 变量与对象关系（重点）

### 5.1 一个「搜索节点」是什么

```python
node = (state, actions)
#        ↑        ↑
#    「我在哪」  「我怎么走过来的」
```

- 起始节点：`(problem.getStartState(), [])`
- 展开一次：`(state, actions)` 经由 `action` 到达 `successor`
  → 新节点 `(successor, actions + [action])`

**每个节点自带完整路径**，所以一旦弹出时命中目标，手上的 `actions` 就是答案。

### 5.2 七个高频名字

| 名字 | 出现位置 | 类型 | 谁产生 | 谁消费 |
|---|---|---|---|---|
| `state` | 函数参数 / 节点元组 | 由 problem 定义（坐标、字符串、元组…） | `getStartState()` / `getSuccessors()[0]` | `isGoalState()` / `getSuccessors()` |
| `successor` | `for` 循环变量 | 同 `state` | `getSuccessors()` | 压栈 / 入队 |
| `action` | `for` 循环变量 | `Directions.NORTH` 等，或测试里的 `'0:A->B'` | `getSuccessors()[1]` | 拼进 `actions`，最终返回 |
| `stepCost` | `for` 循环变量 | `int` / `float` | `getSuccessors()[2]` | UCS/A\* 计算 `g`；DFS/BFS 忽略 |
| `actions` | 你的变量 | `list` | 你自己拼 | 作为返回值交给 Agent |
| `visited` / `closed` | 你的变量 | `set` of `state` | 你维护 | 防止重复扩展（**图搜索**的核心） |
| `heuristic(state, problem)` | A\* 参数 | 数值 | `nullHeuristic` 或你写的 | 估计到目标的剩余代价 |

**`state` 必须不可变**（元组 / 字符串 / `frozenset`）。一旦把 `list` 塞进 `state`，
兄弟分支会共享同一个对象、互相污染——这是本课程最常见的 bug。

### 5.3 三种容器

| 类（`util.py`） | 接口 | 语义 | 用在哪 |
|---|---|---|---|
| `util.Stack` | `push` / `pop` / `isEmpty` | 后进先出（LIFO） | **DFS**（q1） |
| `util.Queue` | `push` / `pop` / `isEmpty` | 先进先出（FIFO） | **BFS**（q2） |
| `util.PriorityQueue` | `push(item, priority)` / `pop` / `update` | 每次弹出代价最小者 | **UCS / A\***（q3 / q4） |

三者接口几乎一致，所以 **q1 → q2 → q3 只需换容器、改优先级**，循环骨架不变。

### 5.4 四种状态空间（本项目的设计核心）

"状态空间怎么设计"决定了搜索是否可行：

| 关卡 | `problem` 类 | `state` 长什么样 | 为什么必须这样 |
|---|---|---|---|
| q1–q4 | `GraphSearch` / `PositionSearchProblem` | `'A'` / `(x, y)` | 只关心"站在哪" |
| q5, q6 | `CornersProblem` | `((x,y), 已访问角落集合)` | 不记角落就会绕圈，永远不知道 4 个角齐了没 |
| q7 | `FoodSearchProblem` | `((x,y), foodGrid)` | 不记剩余豆子就无法判断"全吃完" |
| q8 | `AnyFoodSearchProblem` | `(x, y)` | 目标变成"任意一颗豆"，位置就够 |

### 5.5 一次 DFS 的完整数据流

用例 `test_cases/q1/graph_backtrack.test`：

```
start_state: A      goal_states: G
A 0:A->B B 1.0      A 1:A->C C 2.0
A 2:A->D D 4.0      C 0:C->G G 8.0
```

| 步 | 弹出节点 | 是目标? | visited | 压入 |
|---|---|---|---|---|
| 1 | `('A', [])` | 否 | `{A}` | `('B',[0:A->B])`、`('C',[1:A->C])`、`('D',[2:A->D])` |
| 2 | `('D', [2:A->D])` | 否 | `{A,D}` | 无出边 |
| 3 | `('C', [1:A->C])` | 否 | `{A,D,C}` | `('G',[1:A->C, 0:C->G])` |
| 4 | `('G', [...])` | **是** | — | `return ['1:A->C', '0:C->G']` |

扩展顺序 `A → D → C`，与 `graph_backtrack.solution` 里的 `expanded_states: "A D C"` 一致。

> **"压栈" ≠ "扩展"**：判分器记录的 `expanded_states` 是**调用 `getSuccessors` 的顺序**
> （见 `searchTestClasses.py` 中 `GraphSearch.getSuccessors` 里的 `append`），
> 所以 `if state in visited: continue` 必须写在 `getSuccessors` **之前**，
> 否则重复状态会被记两次。

---

## 6. 八关一览：我实现的函数与位置

每个 `BEGIN … END` 之间就是需要填写的地方，函数定义、docstring、缩进都已给好。

| 关 | 主题 | 文件 | 函数 | 行号 | 分值 |
|---|---|---|---|---|---|
| q1 | 深度优先搜索（图搜索版，非递归） | `search.py` | `depthFirstSearch()` | **L82–L130** | 3 |
| q2 | 宽度优先搜索（图搜索版） | `search.py` | `breadthFirstSearch()` | **L135–L156** | 3 |
| q3 | 一致代价搜索 | `search.py` | `uniformCostSearch()` | **L163–L186** | 3 |
| q4 | A\* 搜索 | `search.py` | `aStarSearch()` | **L198–L224** | 3 |
| q5 | 找到所有角落（状态空间设计） | `searchAgents.py` | `CornersProblem.__init__()` | **L277–L280** | 3 |
| | | | `CornersProblem.getStartState()` | **L287–L290** | |
| | | | `CornersProblem.isGoalState()` | **L298–L301** | |
| | | | `CornersProblem.getSuccessors()` | **L320–L338** | |
| q6 | 角落问题的启发式 | `searchAgents.py` | `cornersHeuristic()` | **L370–L399** | 3 |
| q7 | 吃掉所有豆子（启发式质量） | `searchAgents.py` | `foodHeuristic()` | **L496–L529** | 4 |
| q8 | 次最优搜索 | `searchAgents.py` | `ClosestDotSearchAgent.findPathToClosestDot()` | **L560–L564** | 3 |
| | | | `AnyFoodSearchProblem.isGoalState()` | **L598–L606** | |

> 行号以本仓库文件为准；也可直接搜索 `*** 第N关代码填写位置 ***` 跳转。

### 6.1 关卡依赖（不是每关独立）

`test_cases/qN/CONFIG` 里写着 `depends`：

```
q5  →  depends: q2     判 q5 会先判 q2
q6  →  depends: q4     判 q6 会先判 q4
q7  →  depends: q4     判 q7 会先判 q4
```

含义很实在：**q2 不通过，q5 拿不到分；q4 不通过，q6/q7 拿不到分。**
判分时会先打印 `Note: due to dependencies, the following tests will be run: q2 q5`。

### 6.2 计分方式

| 类型 | 关卡 | 规则 |
|---|---|---|
| `PassAllTestsQuestion` | q1–q5、q8 | 用例全过才给分，错一个就是 0 |
| `Q6PartialCreditQuestion` | q6 | 按各用例 `points` 累加，任一用例硬失败则清零 |
| `PartialCreditQuestion` | q7 | `basePoints(1)` + 每跨过一个 `gradingThresholds` 门槛 +1 |

q7 的门槛是 `15000 12000 9000 7000`（见 `food_heuristic_grade_tricky.test`），
衡量的是 **A\* 在 `trickySearch` 上展开的节点数**——越少越好。

---

## 7. 逐关说明（只讲设计要点与坑）

### q1 深度优先搜索

- 容器：`util.Stack`；`pop()` 出来即"最近压入的"，天然向深处钻。
- 关键：`visited` 查重必须在 `getSuccessors` **之前**。
- 坑：`actions + [action]` 而不是 `actions.append(action)`——后者会让所有分支共享
  同一个 list，互相污染。

### q2 宽度优先搜索

- 与 q1 只差容器：`util.Queue`。
- 目标检测通常改成**入队时**判断，否则 `expanded_states` 会多出节点。
- BFS 在单位代价下天然给出最短路径。

### q3 一致代价搜索

- 容器换成 `util.PriorityQueue`，优先级是**从起点累积的 `g`**。
- `g` 的新值 = 父节点 `g` + `stepCost`，必须一路带着传。
- 节点出队时若已访问则跳过（延迟删除式去重）。

### q4 A\* 搜索

- 优先级 = `g + h(state)`，`h` 由参数 `heuristic=` 传入，默认 `nullHeuristic`（退化成 UCS）。
- 坑：`h` 必须作用在 `state` 上，而不是 `(x, y)` ——q5 起的复合状态尤其要注意。
- 判分含 `astar_3_goalAtDequeue`：目标必须在**出队时**判定，否则可能返回次优路径。

### q5 找到所有角落

- 状态空间是**本关的全部难点**：`(position, visited_corners)`。
- `visited_corners` 必须**每次拷贝或不可变**，否则兄弟分支互相污染。
  典型 bug：`next_corners = state[1]` 是引用而非拷贝，导致只找到 1 个角，
  判分报 `Corners missed: [...]`。
- 目标测试：4 个角全部访问过。

### q6 角落问题的启发式

- 可用 `manhattanHeuristic` / `euclideanHeuristic` 作对照。
- 想拿高分需要"最小生成树"级别的下界，且必须**可采纳 + 一致**。
- 注意：`state` 是 `(position, visited_corners)`，启发式要跳过已访问的角。

### q7 吃掉所有豆子

- 曼哈顿距离在绕墙地图上严重低估（`trickySearch` 上展开 8763 个节点）。
- 换成**真实迷宫距离（BFS）**并缓存 → 展开 1130 个节点，可跨过全部 4 档门槛。
- **MST 下界在这里不可用**：MST 权重对"单点移动"不是 1-Lipschitz，会破坏一致性
  （`food_heuristic_16` 必挂）。这与 TSP 里 MST 可用是两回事，别照搬。
- 缓存挂在 `problem.heuristicInfo` 上，键用规范化的坐标对。

### q8 次最优搜索

- 目标测试在 `AnyFoodSearchProblem.isGoalState`：**踩到任意食物即为目标**。
- 于是 `findPathToClosestDot` 只要**一次 BFS**：BFS 按距离分层扩展，
  第一次碰到食物就是最近的那颗。不需要对每颗豆子分别求距离。
- 坑：返回值必须是 `list`（`return []` 而不是 `return 0`）。

---

## 8. 复现与调试手册

### 8.1 判分

```bash
python run_autograder.py -q q1            # 判一关
python run_autograder.py                  # 判全部
python run_autograder.py -q q1 -p         # 顺带打印每个用例的原始定义
python run_autograder.py -q q1 --mute     # 只看分数
python run_autograder.py -q q5 --no-graphics
```

**只跑单个用例**（路径相对当前目录，必须带 `test_cases/` 前缀）：

```bash
python run_autograder.py -t test_cases/q1/graph_backtrack
```

| 参数 | 作用 |
|---|---|
| `-q` / `--question` | 只判某一关 |
| `-t` / `--test` | 只跑某一个 `.test` |
| `-p` / `--print-tests` | 打印用例定义 |
| `--mute` | 静默，只输出分数 |
| `--no-graphics` | 关闭图形显示 |
| `--generate-solutions` | ⚠️ **危险**，会把当前实现写回 `.solution`，覆盖标准答案 |

> ⚠️ **退出码恒为 0**，即使 0/25。机器判断请 grep 输出里的 `Total:` 或 `Question qN: X/Y`。

### 8.2 图形界面

```bash
python pacman.py -l mediumMaze -p SearchAgent -a fn=dfs
```

| 参数 | 作用 |
|---|---|
| `-l` | 地图名（`layouts/` 下的文件名，不带 `.lay`） |
| `-p` | Agent：`SearchAgent` / `AStarCornersAgent` / `AStarFoodSearchAgent` / `ClosestDotSearchAgent` / `GreedyAgent` / `KeyboardAgent` |
| `-a` | Agent 参数：`fn=`（搜索函数）、`prob=`（问题类）、`heuristic=`（启发式） |
| `-t` | 纯文本逐帧输出（无窗口） |
| `-q` | 不显示，只输出结果 |
| `-z 2` | 窗口放大 2 倍 |
| `--frameTime 0.05` | 每帧停留秒数，`0` = 全速 |
| `-n 3` | 连跑 3 局 |
| `-f` | 固定随机种子，结果可复现 |
| `--timeout 5` | 单次决策超时（秒） |
| `-c` | 捕获异常 / 超时，Agent 崩了不中断整局 |

针对各关的跑法：

```bash
# q1 ~ q4
python pacman.py -l mediumMaze -p SearchAgent -a fn=dfs
python pacman.py -l mediumMaze -p SearchAgent -a fn=astar,heuristic=manhattanHeuristic

# q5 / q6
python pacman.py -l mediumCorners -p SearchAgent -a fn=bfs,prob=CornersProblem
python pacman.py -l mediumCorners -p AStarCornersAgent

# q7
python pacman.py -l trickySearch -p AStarFoodSearchAgent

# q8
python pacman.py -l bigSearch -p ClosestDotSearchAgent --frameTime 0
```

### 8.3 八数码（纯算法验证，不涉及地图）

```bash
python eightpuzzle.py
```

随机生成一个八数码，依次用 BFS、A\*(h1)、A\*(h2) 求解，打印各自的
**路径长度**与**展开节点数**。q2/q4 写完后跑这个，最能直观看出实现是否正确、
启发式是否起作用。

### 8.4 断点调试

`autograder` 是**在当前进程里 import 你的模块**跑的，所以 `print()`、
`breakpoint()`、`pdb` 全部生效，改完直接重跑命令即可，无需重启任何服务。

```bash
# 在代码里插 breakpoint()，然后跑单个用例
python run_autograder.py -t test_cases/q1/graph_backtrack

# 或者直接挂 pdb
python -m pdb run_autograder.py -q q1
```

在 REPL 里手工造题（最细粒度）：

```bash
python -i -c "import search, searchAgents, pacman, layout; gs=pacman.GameState(); gs.initialize(layout.getLayout('mediumMaze'),0); p=searchAgents.PositionSearchProblem(gs); print(len(search.depthFirstSearch(p))); print('expanded =', p._expanded)"
```

### 8.5 常见错误对照

| 输出 | 含义 |
|---|---|
| `The result of X must be a list. (Instead, it is <class 'NoneType'>)` | 函数没 `return`，或走进死路没返回 |
| `... (Instead, it is <class 'tuple'>)` | 返回了状态 / 节点，而不是**动作列表** |
| `Path found with total cost of 999999 ... nodes expanded: 0` | 搜索返回了 `None`（`pacman.py` 的输出里） |
| `Heuristic failed consistency test` | 启发式不一致：`h(s) - h(s') > stepCost` |
| `Heuristic failed admissibility test` | 启发式高估了真实代价 |
| `Corners missed: [...]` | 状态空间没记全角落，或状态被共享污染 |
| `TypeError: object of type 'NoneType' has no len()` | 同上，搜索返回 `None` |
| `ModuleNotFoundError: No module named 'cgi'` | 用了 Python 3.13，换 3.10 |

---

## 9. 注意事项

1. **不要碰 `--generate-solutions`**：它会用当前实现覆盖 `test_cases/**/*.solution`。
   万一需要，先把 `test_cases/` 整个备份。
2. **必须在项目根目录执行**：`test_cases/`、`layouts/` 都是相对路径。
3. **控制台中文乱码**（Windows PowerShell 5.1）：
   ```powershell
   chcp 65001
   $env:PYTHONIOENCODING='utf-8'
   ```
4. **`__pycache__` 会自动重建**，出现莫名其妙的旧行为时，删掉它是最快的排错手段。
5. **`state` 一定要不可变**：`list` 放进 `state` 会让所有分支共享同一个对象。
6. **平台版 `autograder.py` 缺少入口守卫**：文件结尾没有
   `if __name__ == '__main__': main()`，所以直接 `python autograder.py` 会静默退出。
   本仓库的 `run_autograder.py` 只做 `from autograder import main` 后调用一次，
   **不修改 `autograder.py` 本身**，保证与平台行为一致。

---

## 10. 来源与许可

本项目代码源自 **UC Berkeley CS188《Introduction to Artificial Intelligence》的
Pacman 项目（Project 1: Search）**，由该课程改版为中文教学版本并增加了 8 关制判分。
原始版权声明保留在各文件头部：

```
Licensing Information:  You are free to use or extend these projects for
educational purposes provided that (1) you do not distribute or publish
solutions, (2) you retain this notice, and (3) you provide clear
attribution to UC Berkeley, including a link to http://ai.berkeley.edu.

Attribution Information: The Pacman AI projects were developed at UC Berkeley.
The core projects and autograders were primarily created by John DeNero
(denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
Student side autograding was added by Brad Miller, Nick Hay, and
Pieter Abbeel (pabbeel@cs.berkeley.edu).
```

> **关于第 (1) 条 `do not distribute or publish solutions`**：
> 本仓库定位是**个人课程学习留档**——记录自己完成课程作业后的代码，用于复盘与交流，
> 不提供作业代写，也不承接解题请求。若原作者或课程方认为不妥，请联系删除，会立即下架。

`test_cases/`、`layouts/` 等测试数据来自教学版本的公开分发包，随项目一并开源（约 525 KB）。
