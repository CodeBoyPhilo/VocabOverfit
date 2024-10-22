# VocabOverfit

欢迎使用 `VocabOverfit`！这个仓库包含了我在准备 GRE 考试时随意开发的 Streamlit 应用。

**结构**

`main` 分支

此分支包含了部署在 Streamlit 社区云上的应用试用版。

`feat` 分支

此分支包含了应用的完整版本，但因为其独特的用户配置系统无法很好的与Streamlit社区云兼容，所以并未部署在云端。因为我没有软件开发和部署的经验，目前还不知道如何很好的在云端管理和跟踪用户数据。因此，我决定将 `feat` 分支隔离，以便希望体验完整版本的用户可以在本地运行它。

我计划于将app打包分发到PyPI，并上传docker镜像，以便在本地轻松部署

# 内容介绍

## Vocab2Math

[[试用]](https://vocab2math.streamlit.app/)

这个应用帮助你学习和复习词汇。

> [!TIP]
> 对于任何新的词汇列表，我建议至少浏览其两遍。首先选择“Study”模式，记住单词的中文定义，并试着理解词汇公式。然后选择“Revise”模式，试着回忆单词的中文定义，并使用词汇公式作为提示。

## VocabEval

[[试用]](https://vocabeval.streamlit.app/)

这个应用评估你对词汇的掌握情况。

> [!NOTE]
> 应用的试用版仅支持按钮选择答案模式和词汇公式作为选项。完整版应用请转至`feat`分支。

## VocabRevise

这个应用帮助你复习记忆不牢的词汇。这里出现的词汇是你在 `VocabEval` 中答错的词汇。

> [!WARNING]
> 此应用仅在 `feat` 分支中实现

# 致谢

词汇信息来源于 [liurui39660/3000](https://github.com/liurui39660/3000) 和 张巍老师 GRE。

词汇公式由 ChatGPT-4o 生成，并由人工审查以保持公式的质量。

不过，由于词汇来自两个来源，导致定义与公式之间有时会出现释义的不一致。如果你遇到这种情况，或发现定义/公式的展示有错误，请提出 **Issue** 或直接邮件联系作者！
