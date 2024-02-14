# VocabCloud

## 0.0 Prerequisites
`Python` `Neo4j`


## 1.0 Introduction
Extract word embeddings from a list of words input by the user, calculate cosine similarity, and finally generate the data needed to create a word cloud.

## 2.0 Usage Example
The following tutorial will demonstrate the main functionalities using the built-in `GRE 3000` word list.

```python
from toolkit import VocabCloud

cloud = VocabCloud()
``` 

1. **Load Vocabulary Bank**
```python
cloud.load_vocab('GRE') # Load the built-in vocabulary bank from the package
```
If you need to load your own vocabulary bank, make sure the data is in `pandas.DataFrame` format, and must have the following columns: `Vocabulary` `Parts of Speech` `CH-meaning` `EN-meaning`
If a vocabulary has multiple meanings, each meaning should take a unique row.
```python
cloud.load_vocab(my_vocab)
```

2. **Extract Word Embedding**
```python
cloud.create_embedding(model_name='bert-base-uncased')
```
Currently only BERT models are supported. This restriction would be lifted in future versions.
Users can also load their own word embedding vectors. The data should be in `txt` format, with content format same as GloVe embedding
```python
cloud.load_embedding('path/to/my/embedding.txt')
```

3. **Create Graph Data**
```python
cloud.build_df_graph()
cloud.prune_df_graph(threshold=0.9, prune_node=True)
```
`build_df_graph` method would create a `pandas.DataFrame`, including all data needed to generate a word cloud later in Neo4j. 
`prune_df_graph`will delete vocabulary pairs that have similarity score lower than the `threshold` set by the user. If `prune_node` is set `True`, the algorithm would also delete vocabularies that do not have a synonym.

Here, users can also extract the DataFrame and use it directly.
```python
output = cloud.pruned_df_graph
print(output.head())
print(output[output['Vocab_src']=='abandon'])
```

If you need a visualisation of the word cloud, you need to use `Neo4j` and follow the following tutorial

4. **Optional: Using Neo4j to Visualise the Word Cloud**

    **TODO**
