from util import manhattanDistance
from game import Directions
import random, util
from game import Agent


class ReflexAgent(Agent):
    """
    反射型智能体在每个决策点通过状态评估函数检查其可选动作，从而选择一个动作。

    以下代码仅供参考。你可以根据需要随意修改，只要不改动我们的方法头部定义即可。
    """

    def getAction(self, gameState):
        """
        你无需修改此方法，但你也可以修改。
        getAction 根据评估函数从最优选项中作出选择。

        与上一个项目相同，getAction 接收一个 GameState 并返回Directions.X 中的某个值，
        其中 X 属于集合 {NORTH, SOUTH, WEST, EAST, STOP}
        """
        # 收集合法动作和后继状态
        legalMoves = gameState.getLegalActions()

        # 选择最优动作之一
        scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices)
        return legalMoves[chosenIndex]  # 从最优动作中随机选取一个

    def evaluationFunction(self, currentGameState, action):
        """
        在此设计一个更好的评估函数。

        评估函数接收当前状态和候选后继GameState（pacman.py 中定义）并返回一个数值，
        数值越高表示状态越好。

        以下代码从状态中提取了一些有用的信息，例如剩余食物 (newFood) 和移动后 Pacman 的位置 (newPos)。
        newScaredTimes 保存了每个幽灵因 Pacman 吃掉能量豆而处于受惊状态的剩余步数。

        可以打印这些变量查看其内容，然后结合它们创建一个高效的评估函数。
        """

        # 可从 GameState (pacman.py) 中提取的有用信息
        successorGameState = currentGameState.generatePacmanSuccessor(action)
        newPos = successorGameState.getPacmanPosition()
        newFood = successorGameState.getFood()
        newGhostStates = successorGameState.getGhostStates()
        newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]

        # -------------------------- BEGIN --------------------------
        if action == Directions.STOP:
            return -999.0

        # 否则"原地不动"与"必输"同分，无法区分
        if successorGameState.isWin():
            return 999999.0
        if successorGameState.isLose():
            return -999999.0

        # 数据准备
        foodlist = newFood.asList()
        FoodDistance = sorted(util.manhattanDistance(newPos, f) for f in foodlist)
        GhostDistance = sorted(
            util.manhattanDistance(newPos, gs.getPosition()) for gs in newGhostStates
        )

        # 只要有一只幽灵处于受惊状态，就进入"狩猎模式"
        # 原规则的 `0 < t < 39` 会漏掉刚吞下能量豆的那一步（scaredTimer 初始即 40），
        # 结果该追的时候反而掉头逃跑，所以这里放宽为 t > 0
        IsScared = False
        for t in newScaredTimes:
            if t > 0:
                IsScared = True
                break

        # 食物项
        s = 0.0
        if foodlist and FoodDistance[0] > 0:
            s = 1.0 / (FoodDistance[0] ** 4)

        # 分支计算
        d = 5                                  # 危险距离阈值
        GameScore = successorGameState.getScore()

        if not IsScared:
            # ---------- 防守模式：所有幽灵都是威胁 ----------
            nearestGhost = GhostDistance[0] if GhostDistance else 99999.0
            if nearestGhost < d:
                # 分级乘法惩罚：越近惩罚越重
                if nearestGhost <= 1:
                    factor = 0.01              # 贴身，几乎必死
                elif nearestGhost <= 3:
                    factor = 0.3
                else:
                    factor = 0.7
                # 乘法惩罚对负数会反向：-100 * 0.01 = -1，
                # 反而比安全的 -50 更"好"，智能体会主动扑向幽灵。
                # 因此先平移到非负区间再乘、再移回，使该变换保持单调。
                OFFSET = 1000.0
                s = (GameScore + s + OFFSET) * factor - OFFSET
            else:
                s = GameScore + s
        else:
            # ---------- 狩猎模式：受惊幽灵是猎物，未受惊幽灵仍是威胁 ----------
            ScaredGhost = [i for i, t in enumerate(newScaredTimes) if t > 0]
            UnScaredGhost = [i for i, t in enumerate(newScaredTimes) if t == 0]

            s = GameScore + s
            for i in ScaredGhost:
                dist = util.manhattanDistance(newPos, newGhostStates[i].getPosition())
                s += 200.0 / (dist + 1)        # 越近奖励越高
            for i in UnScaredGhost:
                dist = util.manhattanDistance(newPos, newGhostStates[i].getPosition())
                if dist <= 1:
                    s -= 1000.0                # 贴身＝必死
                elif dist < d:
                    s -= 10.0 / dist           # 阈值内温和劝退

        # 判断这一步是否吃到了豆子。
        # 原写法 `if newPos in foodlist` 恒为假——吃掉的那颗已经从 newFood 里移除了，
        # 正确做法是比较移动前后的剩余豆子数。
        if successorGameState.getNumFood() < currentGameState.getNumFood():
            s = s * 1.1

        return s
        # --------------------------  END  --------------------------


def scoreEvaluationFunction(currentGameState):
    """
    此默认评估函数仅返回状态的分数。
    该分数与 Pacman 图形界面中显示的分数相同。

    此评估函数适用于对抗搜索智能体（而非反射型智能体）。
    """
    return currentGameState.getScore()


class MultiAgentSearchAgent(Agent):
    """
    此类为所有多智能体搜索器提供一些通用元素。在此定义的任何方法将可用于
    MinimaxPacmanAgent、AlphaBetaPacmanAgent 和 ExpectimaxPacmanAgent。

    你*无需*在此做任何修改，但若想为所有对抗搜索智能体添加功能，你也可以修改。但请不要删除任何内容。

    注意：这是一个抽象类：不应被实例化。它仅被部分指定，且设计为供继承扩展。
    Agent (game.py)是另一个抽象类。
    """

    def __init__(self, evalFn='scoreEvaluationFunction', depth='2'):
        self.index = 0  # Pacman is always agent index 0 / Pacman 始终是智能体索引 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)


class MinimaxAgent(MultiAgentSearchAgent):
    """
    极小极大智能体（问题 2）
    """

    def getAction(self, gameState):
        """
        使用 self.depth 和 self.evaluationFunction 从当前 gameState返回极小极大最优动作。

        以下是一些在实现极小极大时可能有用的方法调用。

        gameState.getLegalActions(agentIndex)：返回智能体的合法动作列表
        agentIndex=0 表示 Pacman，幽灵的索引 >= 1

        gameState.generateSuccessor(agentIndex, action)：
        返回智能体执行动作后的后继游戏状态

        gameState.getNumAgents()：
        返回游戏中智能体的总数

        gameState.isWin()：
        返回游戏状态是否为胜利状态

        gameState.isLose()：
        返回游戏状态是否为失败状态
        """
        # -------------------------- BEGIN --------------------------
        "*** 第二关代码填写位置 ***"
        # 目标：实现 Minimax 算法。
        # 核心思想：
        # 1. 这是一个递归过程，包含 Pacman (Max层) 和 幽灵 (Min层) 的回合。
        # 2. Max层：Pacman 试图在所有可能的动作中，选择一个能带来最大评估值的动作。
        # 3. Min层：每个幽灵试图在它们所有可能的动作中，选择一个让 Pacman 评估值最小的动作。
        #
        # 实现提示：
        # - 需要创建两个辅助函数：maxVal（处理Pacman的回合）和 minVal（处理幽灵的回合）。
        # - 终止条件：当达到指定搜索深度(self.depth)，或游戏胜利/失败时，停止递归，返回评估函数的值。
        # - 递归逻辑：
        #   - maxVal 调用 minVal。
        #   - minVal 调用 maxVal（如果它是最后一个幽灵）或调用 minVal（传给下一个幽灵）。
        # - 在 getAction 的主函数中，遍历 Pacman 的第一层合法动作，并调用 minVal，找出能获得最高值的动作并返回。
        depth = 0
        bestScore = -float('inf')
        bestAction = Directions.STOP

        legalActions = gameState.getLegalActions(0)
        if Directions.STOP in legalActions:
            legalActions.remove(Directions.STOP)

        for action in legalActions:
            successorState = gameState.generateSuccessor(0, action)
            score = self.minVal(successorState, depth, 1)

            if score > bestScore:
                bestScore = score
                bestAction = action

        return bestAction


    def maxVal(self, gameState, depth):
        # Pacman 回合
        depth += 1

        # 终止条件：达到搜索深度或游戏胜负已定
        if depth == self.depth or gameState.isLose() or gameState.isWin():
            return self.evaluationFunction(gameState)

        value = -9999

        legalActions = gameState.getLegalActions(0)
        if Directions.STOP in legalActions:
            legalActions.remove(Directions.STOP)

        for action in legalActions:
            successorState = gameState.generateSuccessor(0, action)
            value = max(value, self.minVal(successorState, depth, 1))

        return value

    def minVal(self, gameState, depth, index):
        # 幽灵行动前也可能游戏已经结束
        if gameState.isLose() or gameState.isWin():
            return self.evaluationFunction(gameState)

        value = 9999

        legalActions = gameState.getLegalActions(index)
        if Directions.STOP in legalActions:
            legalActions.remove(Directions.STOP)

        for action in legalActions:
            successorState = gameState.generateSuccessor(index, action)

            if index == gameState.getNumAgents() - 1:
                # 最后一个幽灵（总agent数 - pacman个数）后轮到max
                value = min(value, self.maxVal(successorState, depth))
            else:
                # 多个幽灵的情况
                value = min(value, self.minVal(successorState, depth, index + 1))

        return value
        # --------------------------  END  --------------------------


class AlphaBetaAgent(MultiAgentSearchAgent):
    """
    带 alpha-beta 剪枝的极小极大智能体（问题 3）
    """

    def getAction(self, gameState):
        """
        使用 self.depth 和 self.evaluationFunction 返回极小极大最优动作
        """
        # -------------------------- BEGIN --------------------------
        "*** 第三关代码填写位置 ***"
        # 目标：在 Minimax 算法的基础上加入 Alpha-Beta 剪枝。
        # 核心思想：
        # 在搜索过程中，维护两个值 alpha 和 beta。
        # - alpha: Max层(Pacman)到目前为止，能确保获得的最好收益（最小值）。初始为负无穷。
        # - beta: Min层(幽灵)到目前为止，能确保获得的最好收益（最大值）。初始为正无穷。
        # 剪枝规则：
        # 1. 在 Max层，如果当前节点的值大于或等于 beta，则停止搜索该分支（剪枝）。
        # 2. 在 Min层，如果当前节点的值小于或等于 alpha，则停止搜索该分支（剪枝）。
        #
        # 实现提示：
        # - 复制 Minimax 的代码结构。
        # - 为 maxVal 和 minVal 函数增加 alpha 和 beta 两个参数。
        # - 在递归调用时，将 alpha 和 beta 值传递下去。
        # - 在 maxVal 中更新 alpha 值，并检查是否可以进行 beta 剪枝。
        # - 在 minVal 中更新 beta 值，并检查是否可以进行 alpha 剪枝。
        depth = 0
        bestScore = -float('inf')
        bestAction = Directions.STOP

        alpha = -float('inf')
        beta = float('inf')

        
        legalActions = gameState.getLegalActions(0)
        if Directions.STOP in legalActions:
            legalActions.remove(Directions.STOP)
        
        for action in legalActions:
            successorState = gameState.generateSuccessor(0, action)
            score = self.minVal(successorState, depth, 1, alpha, beta)

            # 起始本质也是max节点，使用alpha剪枝
            if score > beta:
                return bestAction
            alpha = max(alpha, score)
        
            if score > bestScore:
                bestScore = score
                bestAction = action
        
        return bestAction
        
        
    def maxVal(self, gameState, depth, alpha, beta):
        # Pacman 回合
        depth += 1
        
        # 终止条件：达到搜索深度或游戏胜负已定
        if depth == self.depth or gameState.isLose() or gameState.isWin():
            return self.evaluationFunction(gameState)
        
        value = -9999
        
        legalActions = gameState.getLegalActions(0)
        if Directions.STOP in legalActions:
            legalActions.remove(Directions.STOP)
        
        for action in legalActions:
            successorState = gameState.generateSuccessor(0, action)
            value = max(value, self.minVal(successorState, depth, 1, alpha, beta))

            # alpha剪枝
            if value > beta:
                return value
            alpha = max(alpha, value)
        
        return value
        
    def minVal(self, gameState, depth, index, alpha, beta):
        # 幽灵行动前也可能游戏已经结束
        if gameState.isLose() or gameState.isWin():
            return self.evaluationFunction(gameState)
        
        value = 9999
        
        legalActions = gameState.getLegalActions(index)
        if Directions.STOP in legalActions:
            legalActions.remove(Directions.STOP)
        
        for action in legalActions:
            successorState = gameState.generateSuccessor(index, action)
        
            if index == gameState.getNumAgents() - 1:
                # 最后一个幽灵（总agent数 - pacman个数）后轮到max
                value = min(value, self.maxVal(successorState, depth, alpha, beta))

                # beta剪枝
                if value < alpha:
                    return value
                beta = min(beta, value)

            else:
                # 多个幽灵的情况
                value = min(value, self.minVal(successorState, depth, index + 1, alpha, beta))

                # beta剪枝
                if value < alpha:
                    return value
                beta = min(beta, value)
        
        return value
        # --------------------------  END  --------------------------


class ExpectimaxAgent(MultiAgentSearchAgent):
    """
    期望极大智能体（问题 4）
    """

    def getAction(self, gameState):
        """
        使用 self.depth 和 self.evaluationFunction 返回期望极大最优动作

        所有幽灵应被建模为从其合法动作中均匀随机选择。
        """
        # -------------------------- BEGIN --------------------------
        "*** 第四关代码填写位置 ***"
        # 目标：实现 Expectimax 算法。
        # 核心思想：
        # 与 Minimax 的主要区别在于 Min 层。这里我们不认为幽灵会做出最优选择，
        # 而是假设它们会从所有合法动作中“随机”选择一个。
        # 1. Max层(Pacman)：与 Minimax 完全相同，仍然选择能获得最大值的动作。
        # 2. Chance层(幽灵)：不再是取最小值，而是计算所有可能后续状态的“期望值”（平均值）。
        #
        # 实现提示：
        # - 将 Minimax 的 `minVal` 函数修改为 `miniExp` (或 `expectedVal`)。
        # - 在 `miniExp` 函数中，遍历幽灵的所有合法动作，递归调用下一层，
        #   将所有返回值累加起来，最后除以合法动作的总数，得到期望值。
        # - `maxiExp` (对应 `maxVal`) 函数逻辑基本不变，但需要返回 (值, 动作) 的元组，以便顶层能获取最佳动作。
        # depth = 0
        # bestScore = -float('inf')
        # bestAction = Directions.STOP
        
        # legalActions = gameState.getLegalActions(0)
        # if Directions.STOP in legalActions:
        #     legalActions.remove(Directions.STOP)
        
        numGhosts = gameState.getNumAgents() - 1
        _, bestAction = self.maxiExp(gameState, self.depth, numGhosts, self.evaluationFunction)
        
        return bestAction
    
    def maxiExp(self, state, depth, numGhosts, func):
        # Pacman 的 Max 层
        if depth == 0 or state.isLose() or state.isWin():
            return func(state), Directions.STOP

        actions = state.getLegalActions(0)
        if Directions.STOP in actions:
            actions.remove(Directions.STOP)
        if not actions:
            return func(state), Directions.STOP

        bestValue = float('-inf')
        bestAction = Directions.STOP

        for action in actions:
            successor = state.generateSuccessor(0, action)
            value = self.miniExp(successor, depth, 1, numGhosts, func)
            if value > bestValue:
                bestValue = value
                bestAction = action

        return bestValue, bestAction

    def miniExp(self, state, depth, ghost, numGhosts, func):
        # 幽灵的 Chance 层
        if state.isLose() or state.isWin():
            return func(state)

        actions = state.getLegalActions(ghost)
        if Directions.STOP in actions:
            actions.remove(Directions.STOP)
        if not actions:
            return func(state)

        v = 0.0
        numActions = len(actions)

        for action in actions:
            successor = state.generateSuccessor(ghost, action)

            if ghost == numGhosts:
                # 最后一个幽灵走完，交回 Pacman，进入max层
                m = self.maxiExp(successor, depth - 1, numGhosts, func)[0]
            else:
                # 还没轮完所有幽灵，交给下一个幽灵，同一深度继续
                m = self.miniExp(successor, depth, ghost + 1, numGhosts, func)

            v += m / numActions

        return v

        # --------------------------  END  --------------------------


def betterEvaluationFunction(currentGameState):
    """
    终极评估函数：猎捕幽灵、收集能量豆、吞食食物、无人能挡（问题 5）。
    """
    # -------------------------- BEGIN --------------------------
    "*** 第五关代码填写位置 ***"
    # 目标：设计一个更高级的线性组合评估函数。
    # 核心思想：
    # 将游戏状态分解为多个“特征”，为每个特征赋予一个权重，然后将它们加权求和。
    # score = w1 * feature1 + w2 * feature2 + ...
    #
    # 建议考虑的特征 (Features) 和权重 (Weights) 提示：
    # 1. 基础分数：`currentGameState.getScore()` 是一个很好的起点。
    # 2. 最近食物距离：与最近食物的距离成反比。例如 `1.0 / minFoodDist`。权重应为正。
    # 3. 剩余食物数量：惩罚项，食物越多，分数越低。例如 `-4 * len(Food)`。权重为负。
    # 4. 幽灵距离：
    #    - 如果幽灵“危险”：距离越近，惩罚越大。例如 `-500 / (dist + 1)`。权重为很大的负数。
    #    - 如果幽灵“受惊”：距离越近，奖励越大。例如 `20 / (dist + 1)`。权重为正。
    # 5. 能量豆距离和数量：鼓励吃豆人去吃能量豆。
    #
    # 请根据以上提示，组合这些特征来计算最终的 `score`。

    # 解包初始数据
    pacmanPos = currentGameState.getPacmanPosition()
    foodList = currentGameState.getFood().asList()
    ghostStates = currentGameState.getGhostStates()
    capsules = currentGameState.getCapsules()

    score = currentGameState.getScore()

    # 觅食特征权重
    if foodList:
        minFoodDist = min([manhattanDistance(pacmanPos, i) for i in foodList])
        score = score + 10.0 / (minFoodDist + 1) - 4.0 * len(foodList)

    # 对抗特征权重
    if ghostStates:
        for ghostState in ghostStates:
            ghost_dist = manhattanDistance(pacmanPos, ghostState.getPosition())
            scared_time = ghostState.scaredTimer

            # 猎捕分支
            if scared_time > 0:
                score += (10.0 - ghost_dist) ** 2

            # 避险分支
            if ghost_dist < 2:
                score -= 500
            elif ghost_dist < 4:
                score -= 50.0 / (ghost_dist + 1)

    # 战略资源权重
    if capsules:
        minCapsuleDist = min([manhattanDistance(pacmanPos, i) for i in capsules])

        if minCapsuleDist < 5:
            score += 5.0 / (minCapsuleDist + 1)

    return score
    # --------------------------  END  --------------------------


# Abbreviation
better = betterEvaluationFunction