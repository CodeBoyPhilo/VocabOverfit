# [:point_right: 中文版README :point_left:](README-ZH.md)

> :warning: **AI Translation**: Some contents in this README file is AI translated with adaption.

# Phi's GRE Prep Toolkit

# 0.0

Welcome to Phi's GRE Prep Toolkit. This repo contains some python gadgets I developed to increase the efficiency of GRE test preparation.
I will update this repo frequently to add some new gadgets I developed. 

# 1.0 What's In Here?

## [VocabCloud](toolkit/VocabCloud/README.md)
**Intro**

VocabCloud is derived from the concepts of Node and Edge. It connects vocabularies that are of similar meaning, so that 'synonyms' or words that are similar  in meaning are eventually connected to form a vocabulary cloud that may help in memorisation/
This is based on BERT, cosine similarity, Page Rank and Community Detection.

**Motivation**

1. Because I often confuse words with similar meanings when memorising them
2. Because I have found, personally, that after becoming familiar with some words of a certain meaning, memorising new words under this meaning becomes very difficult due to the "stereotyped memory" already formed, making the memorisation process of new words quite challenging.

## [Vocab2Math](toolkit/Vocab2Math/README.md)
**Introduction**

Inspired by the famous "Queen = King + Woman - Man" analogy, Vocab2Math aims to generate such an analogy for any input word. Through abstract addition and subtraction, it captures the essence of a vocabulary's meaning.

**Motivation**
1. Merely memorising the meanings of words tends to be easily forgotten and does not facilitate a deep understanding.
2. The formulaic abstract expression captures the underlying meanings of words more effectively, providing a more vivid expression of word meanings.

## [QuestionOverfit](toolkit/QuestionOverfit/README.md)
[`CLI`]((toolkit/QuestionOverfit/README.md))  [`Streamlit`](streamlit/QuestionOverfit/README.md)


**Introduction**

Randomly selecting questions from a question bank for practice and drilling, a process I humorously call "Question Overfitting".
Currently, there are two versions available:
1. The QuestionOverfit API included in the `toolkit` package, usable via command line.
2. A web version deployed on the Streamlit Community Cloud.

**Motivation**
1. The current method of drilling is rather traditional, relying solely on PDF question banks and answers, which is vastly different from the actual exam method, lacking any sense of immersion.
2. I have yet to find a GRE-related drilling and preparation software.
3. Combining these points, I've used the question banks and answers at hand as a basis to develop QuestionOverfit.

# 2.0 Development Plan

1. Improve VocabCloud.
2. Enhance QuestionOverfit.
3. MockGRE
   - Generate practice questions similar to real exam questions based on large language models.
   - Generate a passage containing the input words based on large language models, to aid in the memorisation and understanding of words.




