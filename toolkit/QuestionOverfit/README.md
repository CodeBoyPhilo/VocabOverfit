# QuestionOverfit

## Acknowledgement

The raw questions are sourced from: [张巍老师GRE: Verbal机经1600题](https://mp.weixin.qq.com/s/bPUOg1DyviBpME3xLdTaPA)

## 0.0 Prerequisites
`Python`
`SQLite3`

## 1.0 Introduction

Question drilling and practising via CLI

## 2.0 Usage Example
This tutorial will demonstrate with the built-in `gre_verbal.db` question bank
```python
from toolkit import QuestionOverfit

overfit = QuestionOverfit()
```

1. Load Data. Current version only supports the use of built-in GRE Verbal 1600 question bank
```python
overfit.load_questions()
```

2. Begin Practising
```python
overfit.fit(show=10, difficulty='easy')
```
Here, `show` determines how many questions to sample from the question bank, and `difficulty` determines the difficulty level of the questions.
Users need to use a certain set of interaction commands to interacts with the app. These commands are:

- `next`: move to the next question
- `previous`: move to the previous question
- `to N`: jump to a specific question. Here, the minimal value of N is `1` and the maximum is `show` 
- `exit`: quite practising
- `another round`: based on the current setting of `show` and `difficulty`, do another round of questions. 
- `A`,`B`, ..., `I`: submit answer for single choice questions
- `A, B`, `B, D, I`, etc.: submit answers for multiple choice questions. Choices should be separated by comma `,` plus space ` `. 
