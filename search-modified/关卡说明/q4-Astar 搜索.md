# 第 4 关：A* 搜索

| 项目 | 值 |
|---|---|
| 关卡标识 | `eaypqcwbijko` |
| challenge id | 5809901 |
| 所属实训 | 路径搜索（id 2193187，共 8 关） |
| 分值 | 100 |
| 限时 | 20 分钟 |

## 涉及文件

- `search-modified/search.py`
- `search-modified/game.py`
- `search-modified/pacman.py`
- `search-modified/searchAgents.py`
- `search-modified/util.py`

## 题目正文

---

### 任务描述


本关任务：在 `search.py` 中实现 `A*` 搜索算法，利用启发式函数引导搜索方向，在保证最优性的前提下高效求解路径规划问题。


### 相关知识


为了完成本关任务，你需要掌握：

1. `A*` 搜索；

2. `A*` 的评估函数；

3. `A*` 的搜索流程。

#### A* 搜索

`A*` 搜索（`A-Star Search`，记作 `A*`）是一种典型的有信息搜索算法，其设计思想源自对一致代价搜索（`Uniform Cost Search`, `UCS`）的改进。在 `UCS` 中，节点的扩展顺序仅由从初始状态到当前节点的累计路径代价决定，因此算法只能利用“已知信息”，而无法对未来搜索方向进行判断。`A*` 搜索通过在此基础上引入启发函数，使搜索过程不仅考虑已经发生的实际代价，还能够对从当前节点到目标状态的剩余代价进行估计，从而显著提升搜索效率。

在 `A*` 搜索中，每一个搜索节点都会被赋予一个综合评估代价函数，通常记为
```latex
f(n)=g(n)+h(n)
```
其中，$$g(n)$$ 表示从起始状态到节点 $$n$$ 的**实际累计路径代价**，这一部分与一致代价搜索中的代价定义完全一致；而 $$h(n)$$ 则是启发函数，用于估计从节点 $$n$$ 到目标状态的**最小可能剩余代价**。通过将这两部分信息相结合，`A*` 能够在搜索过程中同时权衡“已经付出的代价”和“未来可能需要付出的代价”。


在节点选择机制上，`A*` 搜索通常使用优先队列作为搜索前沿，并以综合评估代价 $$f(n)$$ 作为节点的优先级。每一次从优先队列中取出的节点，都是当前所有候选节点中 $$f(n)$$ 值最小者。这一选择原则可以概括为：**始终优先扩展综合评估代价最小的节点**。在实际运行过程中，这种机制使搜索过程在保持最优性前提下，大幅减少不必要的节点扩展。


#### A* 的评估函数

当启发函数 $$h(n)$$ 取值恒为零时，综合评估函数退化为
```python
f(n) = g(n)
```
此时，`A*` 搜索在节点选择策略上与一致代价搜索完全一致，即仅依据累计路径代价进行扩展。因此，可以将一致代价搜索视为 `A*` 搜索在零启发条件下的特例。这一退化关系从理论上揭示了 `A*` 与 `UCS` 之间的继承与扩展关系。

启发函数在 `A*` 搜索中的作用主要体现在**引导性与效率提升**两个方面。通过对剩余代价的估计，启发函数能够为搜索过程提供方向性信息，使算法更倾向于探索朝向目标状态的区域，从而减少对明显不优路径的无效扩展。需要强调的是，启发函数并不要求完全准确，只需对真实剩余代价给出一个合理的估计即可；其质量直接影响搜索效率，但并不改变 `A*` 搜索的基本框架。

在具体实现中，启发函数通常作为参数传入搜索算法，并在计算节点优先级时与路径代价相加。例如，新的节点优先级可以通过如下方式计算：

``` python
pathCost = problem.getCostOfActions(goalpath + [action])
pathCost += heuristic(next, problem)
```

其中，`problem.getCostOfActions(goalpath + [action])` 对应于数学定义中的 $$g(n)$$，而 `heuristic(next, problem)` 则对应于 $$h(n)$$。二者相加后得到的 `pathCost` 即为节点的综合评估代价 $$f(n)$$，该值随后被用作优先队列中的排序依据。

#### A* 的搜索流程

A* 搜索在整体结构上与一致代价搜索高度相似，关键区别在于**优先队列的排序依据不同**。

**1. 初始化**

搜索开始时，将初始状态以优先级 0 压入优先队列：

```
new = util.PriorityQueue()
new.push(problem.getStartState(), 0)
```

此时：
```latex
g(s_0) = 0, \quad h(s_0) = heuristic(s_0)
```


------

**2. 节点选择策略**

搜索过程中，每次从优先队列中取出 **f 值最小的节点** 进行扩展：

```
currstate = new.pop()
```

由于优先队列以 `pathCost + heuristic` 作为排序依据，这一步在数据结构层面保证了：
```latex
\forall n \in OPEN,\quad currstate = \arg\min f(n)
```

------

**3. 后继节点扩展与路径维护**

当前节点未被访问过时，将其加入已访问集合，并展开其后继节点：

```python
if currstate not in closed:
    closed.append(currstate)
```

对于每个后继状态 `(next, action, cost)`：

- 先计算实际路径代价 $$g(next)$$
- 再叠加启发函数 $$h(next)$$
- 最终得到综合代价 $$f(next)$$

```python
pathCost = problem.getCostOfActions(goalpath + [action])
pathCost += heuristic(next, problem)
```

随后，将状态和对应路径以 **相同优先级** 压入各自的优先队列：

```python
new.push(next, pathCost)
path.push(goalpath + [action], pathCost)
```

------

**4. 图搜索机制**

`A*` 搜索采用**图搜索**而非树搜索，通过 `closed` 集合避免重复扩展状态：

```python
if currstate not in closed:
    closed.append(currstate)
```

数学上，保证了：
```latex
\forall s \in S,\quad s \text{最多被扩展一次}
```

从而有效避免循环搜索和指数级重复扩展。

### 编程要求

根据提示，在右侧编辑器 `BEGIN-END` 补充代码，在 `search.py` 中实现 `A*` 搜索算法，利用启发式函数引导搜索方向，在保证最优性的前提下高效求解路径规划问题。具体要求如下：

在 `search.py` 中完成以下函数：
```python
def aStarSearch(problem, heuristic=nullHeuristic):

```

返回目标状态的动作序列。

### 测试说明

平台会对你编写的代码进行测试。

**预期输入内容为**：

```python
Question q4
===========
*** PASS: test_cases/q4/astar_0.test
*** 	solution:		['Right', 'Down', 'Down']
*** 	expanded_states:	['A', 'B', 'D', 'C', 'G']
*** PASS: test_cases/q4/astar_1_graph_heuristic.test
*** 	solution:		['0', '0', '2']
*** 	expanded_states:	['S', 'A', 'D', 'C']
*** PASS: test_cases/q4/astar_2_manhattan.test
*** 	pacman layout:		mediumMaze
*** 	solution length: 68
*** 	nodes expanded:		221
*** PASS: test_cases/q4/astar_3_goalAtDequeue.test
*** 	solution:		['1:A->B', '0:B->C', '0:C->G']
*** 	expanded_states:	['A', 'B', 'C']
*** PASS: test_cases/q4/graph_backtrack.test
*** 	solution:		['1:A->C', '0:C->G']
*** 	expanded_states:	['A', 'B', 'C', 'D']
*** PASS: test_cases/q4/graph_manypaths.test
*** 	solution:		['1:A->C', '0:C->D', '1:D->F', '0:F->G']
*** 	expanded_states:	['A', 'B1', 'C', 'B2', 'D', 'E1', 'F', 'E2']

### Question q4: 3/3 ###


Provisional grades
==================
Question q4: 3/3
------------------
Total: 3/3
```

开始你的任务吧，祝你成功！




## 平台参考输出（评测用例）

```
### Question q4: 3/3 ###


Provisional grades
==================
Question q4: 3/3
------------------
Total: 3/3
```
