# Phi's GRE Prep Toolkit

# 0.0
欢迎来到Phi's GRE Prep Toolkit。这个repo包含一些我基于Python做的小玩意，用于提高GRE考试的准备效率。
我会时时更新这个repo，以加入更多有用的小玩意。

# 1.0 这里都有啥？

## [VocabCloud](toolkit/VocabCloud/README-ZH.md)
**Intro**

VocabCloud的主要应用在于利用Node和Edge的概念，将相同含义的单词连接起来，最终形成相似含义单词的词云，以便背诵。基于BERT，cosine similarity，Page Rank和Community Detection

**Motivation**

1. 因为我在本单词的时候时常混淆具有相似含义的单词

2. 因为我发现就我个人而言：当已熟知某个含义下的一些单词后， 遇到这个含义下的新单词时，碍于已经形成的“刻板记忆”，对新单词的记忆过程十分困难

## [Vocab2Math](toolkit/Vocab2Math/README-ZH.md)

**Intro**

受启发于著名的"Queen = King + Woman - Man"对比，Vocab2Math试图给任何一个输入单词生成一个这样的analogy。通过抽象的加减，捕捉单词的含义

**Motivation**
1. 仅背诵单词的含义比较容易忘，且不容易深刻理解
2. 通过公式化的抽象表达，更能捕捉到单词的底层含义，且对于单词含义的表达更为形象。

# 2.0 开发计划

1. 完善VocabCloud
2. QuestionOverfit
    - 根据输入单词快速查找相关的真题
3. MockGRE
   - 基于大语言模型，生成类似真题的practice questions
   - 基于大语言模型，根据输入单词，生成一段包含这些单词的短文，以帮助单词背诵理解