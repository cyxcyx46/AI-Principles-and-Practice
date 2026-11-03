# searchAgents.py
"""
此文件包含可以被选择用来控制 Pacman 的所有智能体。
要选择一个智能体，在运行 pacman.py 时使用 '-p' 选项。
可以使用 '-a' 为智能体传递参数。例如，要加载使用
深度优先搜索 (DFS) 的 SearchAgent，可以运行：

> python pacman.py -p SearchAgent -a fn=depthFirstSearch

其他搜索策略的命令可在项目描述中找到。

请仅修改被要求修改的部分。查找包含

"*** YOUR CODE HERE ***"

的行。  
你需要填写的部分大约在文件下三分之四处。详细说明请参照项目文档。

祝你好运，搜索愉快！
"""

from game import Directions
from game import Agent
from game import Actions
import util
import time
import search

class GoWestAgent(Agent):
    "一个智能体，一直向西移动直到不能移动为止。"

    def getAction(self, state):
        "智能体接收一个 GameState 对象（在 pacman.py 中定义）"
        if Directions.WEST in state.getLegalPacmanActions():
            return Directions.WEST
        else:
            return Directions.STOP

#######################################################
# 这部分代码已经为你写好，但只有在你完成 search.py 的   #
# 对应部分后才能正常工作                               #
#######################################################

class SearchAgent(Agent):
    """
    这个通用搜索智能体使用给定的搜索算法来解决给定的搜索问题，
    然后返回动作序列来沿路径移动。

    默认情况下，该智能体在 PositionSearchProblem 上运行 DFS，
    寻找位置 (1,1)。

    fn 的可选值包括：
      depthFirstSearch 或 dfs
      breadthFirstSearch 或 bfs

    注意：不应修改 SearchAgent 中的任何代码
    """

    def __init__(self, fn='depthFirstSearch', prob='PositionSearchProblem', heuristic='nullHeuristic'):
        # Warning: some advanced Python magic is employed below to find the right functions and problems

        # Get the search function from the name and heuristic
        if fn not in dir(search):
            raise AttributeError(fn + ' is not a search function in search.py.')
        func = getattr(search, fn)
        if 'heuristic' not in func.__code__.co_varnames:
            print(('[SearchAgent] using function ' + fn))
            self.searchFunction = func
        else:
            if heuristic in list(globals().keys()):
                heur = globals()[heuristic]
            elif heuristic in dir(search):
                heur = getattr(search, heuristic)
            else:
                raise AttributeError(heuristic + ' is not a function in searchAgents.py or search.py.')
            print(('[SearchAgent] using function %s and heuristic %s' % (fn, heuristic)))
            # Note: this bit of Python trickery combines the search algorithm and the heuristic
            self.searchFunction = lambda x: func(x, heuristic=heur)

        # Get the search problem type from the name
        if prob not in list(globals().keys()) or not prob.endswith('Problem'):
            raise AttributeError(prob + ' is not a search problem type in SearchAgents.py.')
        self.searchType = globals()[prob]
        print(('[SearchAgent] using problem type ' + prob))

    def registerInitialState(self, state):
        """
        这是智能体第一次看到游戏地图布局。
        在这里，我们选择一条到目标的路径。
        在这一阶段，智能体应该计算到目标的路径并存储在本地变量中。
        所有工作都在这个方法中完成！

        state: 一个 GameState 对象 (pacman.py)
        """
        if self.searchFunction == None: raise Exception("No search function provided for SearchAgent")
        starttime = time.time()
        problem = self.searchType(state) # Makes a new search problem
        self.actions  = self.searchFunction(problem) # Find a path
        totalCost = problem.getCostOfActions(self.actions)
        print(('Path found with total cost of %d in %.1f seconds' % (totalCost, time.time() - starttime)))
        if '_expanded' in dir(problem): print(('Search nodes expanded: %d' % problem._expanded))

    def getAction(self, state):
        """
        返回之前选择路径中的下一个动作（在 registerInitialState 中）。
        如果没有进一步的动作可执行，返回 Directions.STOP。

        state: 一个 GameState 对象 (pacman.py)
        """
        if 'actionIndex' not in dir(self): self.actionIndex = 0
        i = self.actionIndex
        self.actionIndex += 1
        if i < len(self.actions):
            return self.actions[i]
        else:
            return Directions.STOP

class PositionSearchProblem(search.SearchProblem):
    """
    一个搜索问题定义了状态空间、起始状态、目标测试、
    后继函数和代价函数。这个搜索问题可用于找到
    Pacman 板上某个特定点的路径。

    状态空间由 Pacman 游戏中的 (x,y) 坐标组成。

    注意：此搜索问题已完全指定，不应更改。
    """

    def __init__(self, gameState, costFn = lambda x: 1, goal=(1,1), start=None, warn=True, visualize=True):
        """
        Stores the start and goal.

        gameState: A GameState object (pacman.py)
        costFn: A function from a search state (tuple) to a non-negative number
        goal: A position in the gameState
        """
        self.walls = gameState.getWalls()
        self.startState = gameState.getPacmanPosition()
        if start != None: self.startState = start
        self.goal = goal
        self.costFn = costFn
        self.visualize = visualize
        if warn and (gameState.getNumFood() != 1 or not gameState.hasFood(*goal)):
            print('Warning: this does not look like a regular search maze')

        # For display purposes
        self._visited, self._visitedlist, self._expanded = {}, [], 0 # DO NOT CHANGE

    def getStartState(self):
        return self.startState

    def isGoalState(self, state):
        isGoal = state == self.goal

        # For display purposes only
        if isGoal and self.visualize:
            self._visitedlist.append(state)
            import __main__
            if '_display' in dir(__main__):
                if 'drawExpandedCells' in dir(__main__._display): #@UndefinedVariable
                    __main__._display.drawExpandedCells(self._visitedlist) #@UndefinedVariable

        return isGoal

    def getSuccessors(self, state):
        """
        返回后继状态，它们所需的动作，以及代价为 1。

        正如 search.py 中说明：
            对于给定状态，应返回一个三元组列表：
            (successor, action, stepCost)
        其中：
            - successor 是当前状态的后继状态
            - action 是到达该后继状态所需动作
            - stepCost 是扩展到该后继状态的增量代价
        """

        successors = []
        for action in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
            x,y = state
            dx, dy = Actions.directionToVector(action)
            nextx, nexty = int(x + dx), int(y + dy)
            if not self.walls[nextx][nexty]:
                nextState = (nextx, nexty)
                cost = self.costFn(nextState)
                successors.append( ( nextState, action, cost) )

        # Bookkeeping for display purposes
        self._expanded += 1 # DO NOT CHANGE
        if state not in self._visited:
            self._visited[state] = True
            self._visitedlist.append(state)

        return successors

    def getCostOfActions(self, actions):
        """
        Returns the cost of a particular sequence of actions. If those actions
        include an illegal move, return 999999.
        """
        if actions == None: return 999999
        x,y= self.getStartState()
        cost = 0
        for action in actions:
            # Check figure out the next state and see whether its' legal
            dx, dy = Actions.directionToVector(action)
            x, y = int(x + dx), int(y + dy)
            if self.walls[x][y]: return 999999
            cost += self.costFn((x,y))
        return cost

class StayEastSearchAgent(SearchAgent):
    """
    一个位置搜索智能体，使用的代价函数会惩罚在
    游戏板西侧的位置。

    踏入位置 (x,y) 的代价函数是 1/2^x。
    """
    def __init__(self):
        self.searchFunction = search.uniformCostSearch
        costFn = lambda pos: .5 ** pos[0]
        self.searchType = lambda state: PositionSearchProblem(state, costFn, (1, 1), None, False)

class StayWestSearchAgent(SearchAgent):
    """
    一个位置搜索智能体，使用的代价函数会惩罚在
    游戏板东侧的位置。

    踏入位置 (x,y) 的代价函数是 2^x。
    """
    def __init__(self):
        self.searchFunction = search.uniformCostSearch
        costFn = lambda pos: 2 ** pos[0]
        self.searchType = lambda state: PositionSearchProblem(state, costFn)

def manhattanHeuristic(position, problem, info={}):
    "PositionSearchProblem 的曼哈顿距离启发式函数"
    xy1 = position
    xy2 = problem.goal
    return abs(xy1[0] - xy2[0]) + abs(xy1[1] - xy2[1])

def euclideanHeuristic(position, problem, info={}):
    "PositionSearchProblem 的欧几里得距离启发式函数"
    xy1 = position
    xy2 = problem.goal
    return ( (xy1[0] - xy2[0]) ** 2 + (xy1[1] - xy2[1]) ** 2 ) ** 0.5

#####################################################
# This portion is incomplete.  Time to write code!  #
#####################################################

class CornersProblem(search.SearchProblem):
    """
    该搜索问题寻找通过布局中所有四个角的路径。

    你必须选择合适的状态空间和后继函数。
    """

    def __init__(self, startingGameState):
        """
        存储墙壁、Pacman 起始位置和角落信息。
        """
        self.walls = startingGameState.getWalls()
        self.startingPosition = startingGameState.getPacmanPosition()
        top, right = self.walls.height-2, self.walls.width-2
        self.corners = ((1,1), (1,top), (right, 1), (right, top))
        for corner in self.corners:
            if not startingGameState.hasFood(*corner):
                print('Warning: no food in corner ' + str(corner))
        self._expanded = 0 
        
        # DO NOT CHANGE; Number of search nodes expanded
        # Please add any code here which you would like to use
        # in initializing the problem

        "*** 第五关代码填写位置 ***"
        # -------------------------- BEGIN --------------------------
        self.costFn = lambda x: 1

        # --------------------------  END  --------------------------

    def getStartState(self):
        """
        返回起始状态（在你定义的状态空间中，而非完整 Pacman 状态空间）
        """
        "*** 第五关代码填写位置 ***"
        # -------------------------- BEGIN --------------------------
        return (self.startingPosition, [False, False, False, False])

        # --------------------------  END  --------------------------

    def isGoalState(self, state):
        """
        返回该搜索状态是否为问题的目标状态。
        """

        "*** 第五关代码填写位置 ***"
        # -------------------------- BEGIN --------------------------
        return all(state[1])   # 四个角落全被访问（state[1] = [True, True, True, True]返回True）

        # --------------------------  END  --------------------------

    def getSuccessors(self, state):
        """
        返回后继状态，它们所需动作，以及代价为 1。

        正如 search.py 中说明：
            对于给定状态，应返回一个三元组列表：
            (successor, action, stepCost)
        其中：
            - successor 是当前状态的后继状态
            - action 是到达该后继状态所需动作
            - stepCost 是扩展到该后继状态的增量代价
        """

        successors = []
        for action in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:

            "*** 第五关代码填写位置 ***"
            # -------------------------- BEGIN --------------------------
            x, y = state[0]
            next_corners = list(state[1])      # 必须拷贝！否则改的是父状态的那个 list
            dx, dy = Actions.directionToVector(action)
            nextx, nexty = int(x + dx), int(y + dy)
            if not self.walls[nextx][nexty]:
                nextPosition = (nextx, nexty)
                cost = self.costFn(nextPosition)

                if nextPosition in self.corners:
                    idx = self.corners.index(nextPosition)
                    next_corners[idx] = True

                next_state = (nextPosition, next_corners)
                successors.append((next_state, action, cost))
            
        return successors

            # --------------------------  END  --------------------------


    def getCostOfActions(self, actions):
        """
        返回特定动作序列的总代价。如果动作包含非法移动，则返回 999999。
        """
        if actions == None: return 999999
        x,y= self.startingPosition
        for action in actions:
            dx, dy = Actions.directionToVector(action)
            x, y = int(x + dx), int(y + dy)
            if self.walls[x][y]: return 999999
        return len(actions)


def cornersHeuristic(state, problem):
    """
    你为 CornersProblem 定义的启发式函数。

      state: 当前搜索状态
             （你在搜索问题中选择的数据结构）

      problem: CornersProblem 实例

    该函数应始终返回从当前状态到目标状态的最短路径代价的下界；
    即它应该是可采纳的（并且一致）。
    """
    corners = problem.corners # These are the corner coordinates
    walls = problem.walls # These are the walls of the maze, as a Grid (game.py)

    "*** 第六关代码填写位置 ***"
    # -------------------------- BEGIN --------------------------
    def ManhattanDistance(s,c):
        assert isinstance(s, tuple) and isinstance(c, tuple)
        assert len(s) == 2 and len(c) == 2

        return abs(s[0] - c[0]) + abs(s[1] - c[1])

    curr_position = state[0]
    corners = list(corners)        # 用列表记录所有角落（tuple直接索引有问题）
    corner_state = list(state[1])  # 获取角落探索状态

    # 提取未探索角落
    next_corners = [corners[i] for i, cor in enumerate(corners) if not corner_state[i]]
    
    if len(next_corners) == 0:
        return 0

    h = 0
    while len(next_corners) > 0:
        distances = [ManhattanDistance(curr_position, corners) for corners in next_corners]
        min_dist = min(distances)
        min_index = distances.index(min_dist)

        h += min_dist

        curr_position = next_corners.pop(min_index)   # 弹出最小距离角落，并继续累加其它角落

    return h

    # --------------------------  END  --------------------------

class AStarCornersAgent(SearchAgent):
    "用于 CornersProblem 的 A* 搜索智能体，使用你定义的 cornersHeuristic"
    def __init__(self):
        self.searchFunction = lambda prob: search.aStarSearch(prob, cornersHeuristic)
        self.searchType = CornersProblem

class FoodSearchProblem:
    """
    一个搜索问题，目标是找到能够收集 Pacman 游戏中所有食物（点）的路径。

    搜索状态是一个元组 (pacmanPosition, foodGrid)：
      pacmanPosition: Pacman 的位置 (x,y)
      foodGrid:       一个 Grid（见 game.py），True/False 指示剩余食物
    """
    def __init__(self, startingGameState):
        self.start = (startingGameState.getPacmanPosition(), startingGameState.getFood())
        self.walls = startingGameState.getWalls()
        self.startingGameState = startingGameState
        self._expanded = 0 # DO NOT CHANGE
        self.heuristicInfo = {} # A dictionary for the heuristic to store information

    def getStartState(self):
        return self.start

    def isGoalState(self, state):
        return state[1].count() == 0

    def getSuccessors(self, state):
        "Returns successor states, the actions they require, and a cost of 1."
        successors = []
        self._expanded += 1 # DO NOT CHANGE
        for direction in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
            x,y = state[0]
            dx, dy = Actions.directionToVector(direction)
            nextx, nexty = int(x + dx), int(y + dy)
            if not self.walls[nextx][nexty]:
                nextFood = state[1].copy()
                nextFood[nextx][nexty] = False
                successors.append( ( ((nextx, nexty), nextFood), direction, 1) )
        return successors

    def getCostOfActions(self, actions):
        """Returns the cost of a particular sequence of actions.  If those actions
        include an illegal move, return 999999"""
        x,y= self.getStartState()[0]
        cost = 0
        for action in actions:
            # figure out the next state and see whether it's legal
            dx, dy = Actions.directionToVector(action)
            x, y = int(x + dx), int(y + dy)
            if self.walls[x][y]:
                return 999999
            cost += 1
        return cost

class AStarFoodSearchAgent(SearchAgent):
    "用于 FoodSearchProblem 的 A* 搜索智能体，使用你定义的 foodHeuristic"
    def __init__(self):
        self.searchFunction = lambda prob: search.aStarSearch(prob, foodHeuristic)
        self.searchType = FoodSearchProblem
def food_distance(point1, point2, gameState):    
     x1, y1 = point1    
     x2, y2 = point2    
     walls = gameState.getWalls()    
     assert not walls[x1][y1], 'point1 is a wall: ' + str(point1)    
     assert not walls[x2][y2], 'point2 is a wall: ' + str(point2)    
     prob = PositionSearchProblem(gameState, start=point1, goal=point2, warn=False, visualize=False)    
     return len(search.bfs(prob))

def foodHeuristic(state, problem):
    """
    你为 FoodSearchProblem 定义的启发式函数。

    该启发式必须一致以确保正确性。首先尝试提出可采纳启发式；
    几乎所有可采纳启发式也都是一致的。

    如果 A* 找到的解比 UCS 更差，则说明你的启发式
    不一致，可能也不可采纳。  
    但不可采纳或不一致的启发式有时仍可能找到最优解，所以要小心。

    state 是一个元组 (pacmanPosition, foodGrid)，其中 foodGrid 是 Grid
    （见 game.py），True/False 指示食物。你可以用 foodGrid.asList() 获取食物坐标列表。

    如果想访问墙壁、能量胶囊等信息，可以查询 problem。
    例如 problem.walls 给出墙的位置。

    如果想在启发式的多次调用中存储信息，可以使用
    字典 problem.heuristicInfo。例如，你只想计算一次墙的数量：
    problem.heuristicInfo['wallCount'] = problem.walls.count()
    后续调用可访问 problem.heuristicInfo['wallCount']
    """
    position, foodGrid = state
    
    
    "*** 第七关代码填写位置 ***"
    # -------------------------- BEGIN --------------------------
    foods = foodGrid.asList()

    if not foods:
        return 0

    info = problem.heuristicInfo
    cache = info.setdefault('maze_dist', {})

    def maze_dist(a, b):
        """真实迷宫距离（BFS），带缓存：同一对坐标只算一次（用曼哈顿距离会炸掉）"""
        key = (a, b) if a <= b else (b, a)
        if key not in cache:
            prob = PositionSearchProblem(problem.startingGameState, goal=b, start=a,
                                         warn=False, visualize=False)
            cache[key] = len(search.bfs(prob))
        return cache[key]

    # 当前位置到「最远」食物的真实距离
    #   移动一格，每项最多变 1，取 max 后仍最多变 1 -> 1-Lipschitz
    h = max(maze_dist(position, f) for f in foods)

    # 食物两两之间的最大真实距离
    #   与 pacman 位置无关；吃掉食物时集合变小，且被吃掉的边
    #   d(f,x)=d(新位置,x) 会被分量 1 接管，所以不会突变
    for i in range(len(foods) - 1):
        for j in range(i + 1, len(foods)):
            d = maze_dist(foods[i], foods[j])
            if d > h:
                h = d

    return h

    # --------------------------  END  --------------------------

class ClosestDotSearchAgent(SearchAgent):
    "通过一系列搜索寻找所有食物的智能体"
    def registerInitialState(self, state):
        self.actions = []
        currentState = state
        while(currentState.getFood().count() > 0):
            nextPathSegment = self.findPathToClosestDot(currentState) # The missing piece
            self.actions += nextPathSegment
            for action in nextPathSegment:
                legal = currentState.getLegalActions()
                if action not in legal:
                    t = (str(action), str(currentState))
                    raise Exception('findPathToClosestDot returned an illegal move: %s!\n%s' % t)
                currentState = currentState.generateSuccessor(0, action)
        self.actionIndex = 0
        print('Path found with cost %d.' % len(self.actions))

    def findPathToClosestDot(self, gameState):
        """
        Returns a path (a list of actions) to the closest dot, starting from
        gameState.
        """
        # Here are some useful elements of the startState
        startPosition = gameState.getPacmanPosition()
        food = gameState.getFood()
        walls = gameState.getWalls()
        problem = AnyFoodSearchProblem(gameState)

        "*** 第八关代码填写位置 ***"
        # -------------------------- BEGIN --------------------------
        # 一次 BFS 就够，不需要对每个食物分别求距离再取 min，
        return search.breadthFirstSearch(problem)
        
        # --------------------------  END  --------------------------

class AnyFoodSearchProblem(PositionSearchProblem):
    """
    用于寻找任意一个食物路径的搜索问题。

    这个问题与 PositionSearchProblem 类似，但目标测试不同，
    你需要在下面实现。状态空间和后继函数不需要更改。

    该类继承了 PositionSearchProblem 的方法。

    你可以使用这个搜索问题来实现 findPathToClosestDot 方法。
    """

    def __init__(self, gameState):
        "存储来自 gameState 的信息。你不需要更改这一部分。"

        # Store the food for later reference
        self.food = gameState.getFood()

        # Store info for the PositionSearchProblem (no need to change this)
        self.walls = gameState.getWalls()
        self.startState = gameState.getPacmanPosition()
        self.costFn = lambda x: 1
        self._visited, self._visitedlist, self._expanded = {}, [], 0 # DO NOT CHANGE

    def isGoalState(self, state):
        """
        状态是 Pacman 的位置。请在这里填入一个目标测试，
        以完整定义该搜索问题。
        """
        x,y = state

        "*** 第八关代码填写位置 ***"
        # -------------------------- BEGIN --------------------------
        foodGrid = self.food

        if foodGrid[x][y] == True:
            return True
        else:
            return False

        # --------------------------  END  --------------------------
