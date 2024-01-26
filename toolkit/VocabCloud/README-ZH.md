# VocabCloud

## 0.0 Prerequisites
`Python`

`Neo4j`


## 1.0 Introduction
根据用户输入的单词表，提取word embedding，计算cosine similarity，最后生成制作词云所需要的数据

## 2.0 Usage Example
以下教程将使用包自带的`GRE 3000`词库进行主要功能示范

```python
from toolkit import VocabCloud

cloud = VocabCloud()
``` 

1. **加载词表**
```python
cloud.load_vocab('GRE') # 加载包自带的GRE 300 词库
```
如果需要加载自己的词库，则需要将自行将词库转换成`pandas.DataFrame`格式，且用有以下列：`Vocabulary` `Parts of Speech` `CH-meaning` `EN-meaning`
同一个单词具有多个含义的话，需每一个含义单独占一行
```pycon
cloud.load_vocab(my_vocab)
```

2. **提取Word Embedding**
```python
cloud.create_embedding(model_name='bert-base-uncased')
```
目前代码仅支持BERT系列模型。将在未来版本减少该限制。
用户也可以加载自己的Word Embedding。文件格式需为`txt`格式，格式同GloVe embedding
```python
cloud.load_embedding('path/to/my/embedding.txt')
```

3. **创建Graph Data**
```python
cloud.build_df_graph()
cloud.prune_df_graph(threshold=0.9, prune_node=True)
```
`build_df_graph`方法将创建一个pandas.DataFrame，包含一系列生成词云所需的数据。
`prune_df_graph`将根据用户设置的`threshold`门槛，剔除相似度在次之下的单词对。如果`prune_node`等于`True`，算法也将剔除没有近似词的单词，
以保证最后的DataFrame仅包含有一个或多个近似词的单词

至此，用户已可以直接将DataFrame提取出来并使用。
```python
output = cloud.pruned_df_graph
print(output.head())
print(output[output['Vocab_src']=='abandon'])
```
如果需要利用`Neo4j`创建词云，请参考以下教程

4. **Optional: 使用Neo4j可视化词云**

    **TODO**
