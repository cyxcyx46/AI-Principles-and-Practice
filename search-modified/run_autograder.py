#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地调试入口。

平台提供的 autograder.py 结尾缺少 `if __name__ == '__main__': main()`，
直接 `python autograder.py -q q1` 不会有任何输出。这个文件只是补一个入口，
不修改 autograder.py 本身，因此和平台上跑的行为保持一致。

用法（和原生 autograder 相同）：
    python run_autograder.py -q q1          # 判某一关
    python run_autograder.py -q q1 --no-graphics
    python run_autograder.py                # 判全部
"""
import sys

from autograder import main

if __name__ == '__main__':
    sys.exit(main())
