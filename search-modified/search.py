# search.py
"""
在 search.py 中，你将实现通用的搜索算法，
这些算法会被 Pacman 智能体（在 searchAgents.py 中）调用。
"""
# from fontTools.misc.cython import returns

import util

class SearchProblem:
    """
    这个类描述了一个搜索问题的结构，但并没有实现任何具体方法
    （在面向对象术语中：这是一个抽象类）。

    你不需要、也不应该对这个类做任何修改。
    """

    def getStartState(self):
        """
        返回搜索问题的初始状态。
        """
        util.raiseNotDefined()

    def isGoalState(self, state):
        """
        tate: 搜索状态

        当且仅当该状态是一个合法的目标状态时，返回 True。
        """
        util.raiseNotDefined()

    def getSuccessors(self, state):
        """
        state: 搜索状态

        对于给定的状态，该函数应返回一个三元组列表：
        (successor, action, stepCost)

        其中：
        - successor 是当前状态的一个后继状态
        - action 是到达该后继状态所需采取的动作
        - stepCost 是从当前状态扩展到该后继状态的增量代价
        """
        util.raiseNotDefined()

    def getCostOfActions(self, actions):
        """
        actions: 一个要执行的动作序列（列表）

        该方法返回执行该动作序列的总代价。
        该动作序列必须全部由合法动作组成。
        """
        util.raiseNotDefined()


def tinyMazeSearch(problem):
    """
    返回一组可以解决 tinyMaze 的动作序列。
    对于任何其他迷宫，这个动作序列都是不正确的，
    因此该函数只能用于 tinyMaze。
    """
    from game import Directions
    s = Directions.SOUTH
    w = Directions.WEST
    return  [s, s, w, s, w, w, s, w]

def depthFirstSearch(problem):
    """
    优先搜索搜索树中最深的节点。

    你的搜索算法需要返回一组动作列表，以到达目标状态。
    确保实现的是一个图搜索算法（Graph Search）。

    入门时，你可以尝试以下简单命令来理解传入的搜索问题：

    print("起始状态:", problem.getStartState())
    print("起始状态是否是目标状态?", problem.isGoalState(problem.getStartState()))
    print("起始状态的后继节点:", problem.getSuccessors(problem.getStartState()))
    """

    "*** 第一关代码填写位置 ***"
    # -------------------------- BEGIN --------------------------

    # ===== 三个角色，先认清楚 =====
    #   problem : 搜索问题，只提供 4 个方法（你只能调用，不能改）
    #             - getStartState()                  -> 起始状态 state
    #             - isGoalState(state)               -> True/False
    #             - getSuccessors(state)             -> [(后继状态, 动作, 代价), ...]
    #             - getCostOfActions(actions)        -> 动作序列总代价（DFS 用不到）
    #   state   : 状态。它长什么样完全由 problem 决定
    #             （pacman 里是坐标 (x, y)，图搜索里是 'A'/'B' 这种字符串）
    #   actions : 动作序列，从起始状态走到 state 依次做的动作组成的 list。
    #             注意「动作」对 DFS 是不透明的符号，我们不解释它，只管拼起来。

    # 容器：栈 = 后进先出，这决定了 DFS「一路往深处钻」的行为
    stack = util.Stack()

    # 搜索节点 = (state, actions)，即「我现在在哪」+「我是怎么走到这儿的」。
    # 起始状态的 actions 是空列表：还没走任何一步。
    stack.push((problem.getStartState(), []))

    # 图搜索的关键：记住已经扩展过的 state，避免重复扩展。
    # 用 set 而不是 list，因为 set 查重是 O(1)。
    visited = set()

    while not stack.isEmpty():
        # 弹栈：最近压进去的节点最先出来 -> 深度优先
        state, actions = stack.pop()

        # 目标检测放在「出栈时」而不是「入栈时」，保证返回的就是当前这条路径
        if problem.isGoalState(state):
            return actions

        # 同一个状态可能被不同路径重复压栈，扩展前先查重
        if state in visited:
            continue

        visited.add(state)

        # 展开：每个后继都可能成为下一步
        for successor, action, stepCost in problem.getSuccessors(state):
            if successor not in visited:
                # 关键一步——把「走到 successor 的动作」接到当前路径尾巴上，
                # 这样每个节点自己就带着从起点到它的完整动作序列
                stack.push((successor, actions + [action]))

    # 栈空了还没找到，说明目标不可达，按约定返回空列表
    return []

    # --------------------------  END  --------------------------


def breadthFirstSearch(problem):
    "*** 第二关代码填写位置 ***"
    # -------------------------- BEGIN --------------------------
    queue = util.Queue()
    queue.push((problem.getStartState(), []))

    visited = []   # list不可哈希
    while not queue.isEmpty():
        state, actions = queue.pop()

        if problem.isGoalState(state):
            return actions

        if state in visited:
            continue

        visited.append(state)

        for successor, action, cost in problem.getSuccessors(state):
            if successor not in visited:
                queue.push((successor, actions + [action]))

    return []
    # --------------------------  END  --------------------------



def uniformCostSearch(problem):
    """优先搜索总代价最小的节点。"""
    "*** 第三关代码填写位置 ***"
    # -------------------------- BEGIN --------------------------
    pri_queue = util.PriorityQueue()
    pri_queue.update((problem.getStartState(), []), 0)   # 优先级队列：push((state, action), cost)

    visited = set()

    while not pri_queue.isEmpty():
        state, actions = pri_queue.pop()
        pathcosts = problem.getCostOfActions(actions)   # 获取当前路径的cost

        if problem.isGoalState(state):
            return actions

        if state in visited:
            continue

        visited.add(state)

        for successor, action, cost in problem.getSuccessors(state):
            if successor not in visited:
                pri_queue.update((successor, actions + [action]), pathcosts + cost)   # 同步更新cost判定优先级

    return []
    # --------------------------  END  --------------------------

def nullHeuristic(state, problem=None):
    """
    启发式函数用于估计从当前状态到所提供搜索问题中的最近目标的代价。
    这个启发式函数是最简单的（平凡的）。
    """
    return 0

def aStarSearch(problem, heuristic=nullHeuristic):
    """优先搜索总代价与启发式函数值之和最小的节点。"""
    "*** 第四关代码填写位置 ***"
    # -------------------------- BEGIN --------------------------
    pri_queue = util.PriorityQueue()  #  通过优先级队列求g(n)
    pri_queue.update((problem.getStartState(), []), 0)
    
    visited = []
    
    while not pri_queue.isEmpty():
        state, actions = pri_queue.pop()
        cost_now = problem.getCostOfActions(actions)
    
        if problem.isGoalState(state):
            return actions
    
        if state in visited:
            continue
    
        visited.append(state)
    
        for successor, action, cost in problem.getSuccessors(state):
            if successor not in visited:
                g = cost_now + cost
                h = heuristic(successor, problem)       #  h根据传入的problem确定，不一定为0
                f = g + h
                pri_queue.update((successor, actions + [action]), f)
    
    return []
    # --------------------------  END  --------------------------

# Abbreviations
bfs = breadthFirstSearch
dfs = depthFirstSearch
astar = aStarSearch
ucs = uniformCostSearch
