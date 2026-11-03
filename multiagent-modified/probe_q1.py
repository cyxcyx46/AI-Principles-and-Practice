#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第一关探针：把 ReflexAgent.evaluationFunction 能拿到的所有变量打印出来，
用来搞清楚「变量是什么类型」和「接口怎么一步步串起来」。

运行：
    cd Z:\\workspace\\multiagent-modified
    conda activate multiagent-modified
    python probe_q1.py

这个文件不参与判分（判分只加载 multiAgents.py），只是学习/调试用的观察窗口。
"""
import random

import layout
import pacman
import util
from game import Directions
from multiAgents import ReflexAgent

random.seed(0)

lay = layout.getLayout('openClassic')
state = pacman.GameState()
state.initialize(lay, numGhostAgents=1)

line = '=' * 72

print(line)
print('① Agent 直接拿到的是 GameState 对象')
print(line)
print('类型                    :', type(state).__module__ + '.' + type(state).__name__)
print('getPacmanPosition()     :', state.getPacmanPosition(), ' <- 元组 (x, y)')
print('getScore()              :', state.getScore())
print('getNumFood()            :', state.getNumFood())
print('isWin() / isLose()      :', state.isWin(), '/', state.isLose())

print()
print(line)
print('② 食物：getFood() 返回的是 Grid 二维网格，不是 list')
print(line)
food = state.getFood()
print('类型                    :', type(food).__module__ + '.' + type(food).__name__)
print('尺寸 width x height     :', food.width, 'x', food.height, ' <- 注意 Grid 是 [x][y]')
foodList = food.asList()
print('asList() 前 5 个        :', foodList[:5])
print('asList() 总数           :', len(foodList), '（= getNumFood()）')
fx, fy = foodList[0]
print('food[%d][%d]            :' % (fx, fy), food[fx][fy], ' <- True 表示这一格有豆子')
print('food[%d][%d]            :' % (fx, fy), food[fx][fy - 1], ' <- 相邻格没有就是 False')

print()
print(line)
print('③ 幽灵：getGhostStates() 返回 GhostState 列表')
print(line)
ghostStates = state.getGhostStates()
print('个数                    :', len(ghostStates))
for i, gs in enumerate(ghostStates):
    print('  [%d] 类型              :' % i, type(gs).__name__)
    print('      getPosition()     :', gs.getPosition(), ' <- 和 pacman 同一套 (x, y) 坐标')
    print('      getDirection()    :', gs.getDirection())
    print('      scaredTimer       :', gs.scaredTimer, '（>0 表示处于受惊状态，可被吃）')
    print('      isPacman          :', gs.isPacman)

print()
print(line)
print('④ 接口链路：getAction -> generatePacmanSuccessor -> evaluationFunction')
print(line)
print('ReflexAgent.getAction 的逻辑（平台已给定，第 23-30 行）：')
print('    legalMoves = gameState.getLegalActions()')
print('    scores = [self.evaluationFunction(gameState, action) for action in legalMoves]')
print('    bestScore = max(scores)  → 在分数最高的动作里随机挑一个')
print()
agent = ReflexAgent()
agent.index = 0

legalMoves = state.getLegalActions()
print('getLegalActions()       :', legalMoves)
print()
print('  动作            后继位置        剩余豆子   分数    evaluationFunction')
print('  ' + '-' * 68)
for act in legalMoves:
    succ = state.generatePacmanSuccessor(act)
    score = agent.evaluationFunction(state, act)
    print('  %-12s %-14s %-10s %-7s %.3f' % (
        act, str(succ.getPacmanPosition()), succ.getNumFood(), succ.getScore(), score))

print()
print(line)
print('⑤ 两个最常用的距离/查表工具（util.py）')
print(line)
p = state.getPacmanPosition()
g = state.getGhostStates()[0].getPosition()
print('当前 pacman 位置        :', p)
print('幽灵位置               :', g)
print('util.manhattanDistance :', util.manhattanDistance(p, g))
print()
print('注意：本关地图没有墙体时曼哈顿距离≈真实步数；')
print('      有墙时必须绕路，曼哈顿距离会低估——这是启发式常见失真的来源。')

print()
print(line)
print('⑥ 吃能量豆前后的区别（scaredTimer 的作用）')
print(line)
capsules = state.getCapsules()
print('getCapsules()           :', capsules, ' <- 能量豆位置（吃掉后幽灵受惊）')
print('当前 scaredTimer        :', [gs.scaredTimer for gs in ghostStates])
print()
print('受惊时：幽灵变成「行走的 200 分」，应该主动靠近（距离越近评估值越高）')
print('未受惊：幽灵是死亡陷阱，应该远离（贴身时给致命负分）')
