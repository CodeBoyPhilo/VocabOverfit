# Vocab2Math

## Developing

This feature is still under development. Currently the code and model for my very first attempt is uploaded and is only a placeholder.

Records of My First Attempt:

**Main Assumptions**

The three vocabularies on the RHS of the formula are deeply connected to the vocabulary on LHS, and they are synonyms or vocabularies that have contrary meanings

**Main Ideology**

Based on the main assumptions, we can see the RHS vocabs are the LHS vocab being uniquely transformed three times.

For example:
`handsome` would transform to `attractive`

The most straightforward model that learns this type of transformation is a Neural Network. I have created a very naive and simple model in `model.py`. The model would output a $1 \times N$ tensor, where $N$ depends on
the length of the embedding vector. I then use the negated cosine similarity to train the model. 

The result is disappointing. However, I personally found this attempt very entertaining, since I am looking for three universal transformation functions with three sets of weights that would be suitable for all vocabularies.
