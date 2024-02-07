# QuestionOverfit

## Acknowledgement

原始题目数据源于： [张巍老师GRE: Verbal机经1600题](https://mp.weixin.qq.com/s/bPUOg1DyviBpME3xLdTaPA).


## 0.0 Prerequisites

`Python`
`SQLite3`

## 1.0 Introduction

基于命令行进行刷题

## 2.0 Usage Example
以下教程将使用包自带的`gre_verbal.db`题库进行主要功能示范
```python
from QuestionOverfit import QuestionOverfit
overfit = QuestionOverfit()
```

1. 加载数据。当前版本仅支持使用包自带的GRE Verbal 1600题库
```python
overfit.load_questions()
```
2. 开始刷题
```python
overfit.fit(show=10, difficulty='easy')
```
此处，`show`决定了要从题库中抽取多少道题，`difficulty`决定了这些题目的难度等级
用户需要使用特定的命令与程序交互。这些命令为：

- `next`: 转到下一道题
- `previous`: 转到上一道题
- `to N`: 转到特定的一道题。这里N的最小值为`1`，最大值为`show`的值
- `exit`: 结束刷题
- `another round`: 根据现在输入的`show`与`difficulty`，再来一轮题。只有当用户输入`another round`时，才会sample without replacement
- `A`,`B`, ..., `I`: 单选题提交答案
- `A, B`, `B, D, I`, etc.: 多选题提交答案。选项之间应使用`,`加空格` `隔开
