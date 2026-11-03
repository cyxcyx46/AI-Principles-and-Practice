#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""验证这套规则里的逻辑问题（每条都给出可复现的数字）"""
import random
import layout
import pacman
import util
from game import Directions

print('=' * 74)
print('问题 1：乘法惩罚在负分时会把"危险"算成"更好"')
print('=' * 74)
base_danger = -100.0   # 贴着幽灵的一步
base_safe = -50.0      # 安全处的一步
print('贴幽灵 base = %-7s 直接乘 0.01 -> %-8s' % (base_danger, base_danger * 0.01))
print('安全处 base = %-7s 直接乘 0.01 -> %-8s' % (base_safe, base_safe * 0.01))
print('判定：%s > %s  → 贴幽灵反而得分更高 ✗ 智能体会主动扑向幽灵'
      % (base_danger * 0.01, base_safe * 0.01))
OFFSET = 1000.0
off_d = (base_danger + OFFSET) * 0.01 - OFFSET
off_s = (base_safe + OFFSET) * 0.01 - OFFSET
print('偏移保护后：%s vs %s → 顺序正确 ✓' % (round(off_d, 1), round(off_s, 1)))

print()
print('=' * 74)
print('问题 2：能量豆吃下的那一步 scaredTimer = 40，`0 < t < 39` 判定不到')
print('=' * 74)
random.seed(0)
lay = layout.getLayout('openClassic')
state = pacman.GameState()
state.initialize(lay, numGhostAgents=1)

capsule = state.getCapsules()[0]
print('能量豆位置:', capsule)
# 直接构造"刚吃掉能量豆"的幽灵状态，观察 scaredTimer
ghost = state.getGhostStates()[0]
saved = ghost.scaredTimer
ghost.scaredTimer = 40          # 吃掉能量豆那一刻平台就是置 40
print('刚吃下能量豆时 scaredTimer =', ghost.scaredTimer)
print('  规则 `0 < t < 39` 判定受惊吗 ?', 0 < ghost.scaredTimer < 39, '  → 判为「不受惊」，掉头逃跑 ✗')
print('  修正 `t > 0`      判定受惊吗 ?', ghost.scaredTimer > 0, '   → 判为「受惊」，主动追击 ✓')
ghost.scaredTimer = saved

print()
print('=' * 74)
print('问题 3：`if newPos in foodlist` 是死代码，永远不成立')
print('=' * 74)
foodNow = state.getFood().asList()
pac = state.getPacmanPosition()
print('pacman 位置:', pac, ' 剩余豆子:', len(foodNow))


def walk_to_food(st, max_steps=200):
    """朝最近食物走，直到出现「走这一步会吃到豆子」的局面"""
    cur = st
    for _ in range(max_steps):
        foods = cur.getFood().asList()
        if not foods:
            return None
        for act in cur.getLegalActions():
            succ = cur.generatePacmanSuccessor(act)
            p = succ.getPacmanPosition()
            if cur.getFood()[p[0]][p[1]] and succ.getNumFood() < cur.getNumFood():
                return cur, act, succ
        # 不然就朝最近食物走一步
        best_act, best_d = None, None
        for act in cur.getLegalActions():
            p = cur.generatePacmanSuccessor(act).getPacmanPosition()
            dmin = min(util.manhattanDistance(p, f) for f in foods)
            if best_d is None or dmin < best_d:
                best_act, best_d = act, dmin
        cur = cur.generatePacmanSuccessor(best_act)
        if cur.isLose():
            return None
    return None


found = walk_to_food(state)
if found:
    before, act, succ = found
    newPos = succ.getPacmanPosition()
    newFood = succ.getFood().asList()
    print('找到吃豆的一步：动作 %s' % act)
    print('  吃之前剩余豆子 %d -> 吃之后 %d' % (before.getNumFood(), succ.getNumFood()))
    print('  新位置 newPos =', newPos)
    print('  newPos in newFood(后继 asList) =', newPos in newFood,
          '  → 恒为 False，×1.1 永不触发 ✗')
    print('  newPos in food(移动前 asList) =', newPos in before.getFood().asList(),
          '  → True，说明该比较「移动前」或用豆子数差 ✓')
    print('  getNumFood 减少判定 =', succ.getNumFood() < before.getNumFood(), ' → True ✓')
else:
    print('（没走到吃豆局面）')

print()
print('=' * 74)
print('问题 4：返回 `a` 会把评估函数变成常量')
print('=' * 74)
print('a = 200.0 只是"受惊幽灵"的权重。若最终 return a，')
print('则所有动作的评估值都相同 → getAction 在并列里随机选 → 等于瞎走 ✗')
