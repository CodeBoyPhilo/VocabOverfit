# Vocab2Math

## 施工中

目前本项目还在开发中，第一次尝试的代码与模型已上传，仅做占位使用。

第一次尝试记录：

**主要假设**

公式内的三个单词与输入单词存在联系，为含义相近或相反的单词

**主要逻辑**

根据主要假设，我们可以将公式内三个单词想像成输入单词在进过三次transformation后得到的单词。
例如：handsome在某种转换后变为attractive。

可学习这种转换关系的最直接的模型即神经网络。我在`model.py`中创建了一个简单的模型架构，最终模型将输出一个 $1\times N$的tensor，$N$取决于Embedding
Vector的长度。最终通过Negated Cosine Similarity训练模型。

本次尝试效果十分拉垮

