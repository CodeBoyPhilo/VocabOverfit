# [:point_right: 中文版README :point_left:](README-ZH.md)

# VocabOverfit

Welcome to `VocabOverfit`! This repo contains the streamlit apps that I casually devloped when preparing for my GRE exam.

**Structure**

`main` branch

This branch contains the try-it-out version of the apps that are deployed on Streamlit Community Cloud.

`feat` branch

This branch contains the full version of the apps that are updated frequently, however, not deployed on the cloud yet due to the additional user profile feature. Since I have no software development experiments nor do I have any deployment experience, currently I have no clue how to manage and track user data on cloud. Therefore I decided to insulate the `feat` branch for anyone that wish to experience the full version to run it locally.

However, a packaged version distributing to PyPI and a docker image is coming soon for easy local deployment (as soon as I tested the app on different platform)

# What's In Here?

## Vocab2Math

[[try-it-out]](https://vocab2math.streamlit.app/)

The app that helps you study and revise the vocabularies.

> [!TIP]
> For any new vocabulary list, I recommend you to go through it at least twice. Select `Study` mode first and memorise the Chinese definition of the word, and try to make sense of the vocab equations. Select `Revise` mode next, try to recall the Chinese definition of the word, and use the vocab equations as the hints.

## VocabEval

[[try-it-out]](https://vocabeval.streamlit.app/)

The app that evaluates your knowledge about the vocabularies.

> [!NOTE]
> The try-it-out version of the app only supports button-selection answer mode and vocab equations as the answer set. Please refer to the app under the `feat` branch for a full version of the app.

## VocabRevise

The app that helps you revise for the ill-memorised vocabularies. The vocabularies appear here are those that you wrongly answered in `VocabEval`.

> [!WARNING]
> This app is only implemented in the `feat` branch

# Acknowledgement

The vocabulary details are adapted from [liurui39660/3000](https://github.com/liurui39660/3000) and 张巍老师GRE.

The vocabulary equations are generated using ChatGPT-4o with Human-in-the-loop to maintai the quality of the equations.

However, since the vocabularies come from two sources, there are cases of conflicts between the definitions and equations. If you encounter such cases or there appears to be errors in the presentation of the definitions/equations, please raise an **Issue** or email the author directly!
