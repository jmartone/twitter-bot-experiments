# twitter-bot-experiments

A basic Twitter bot that employs the [Twitter Streaming API](https://dev.twitter.com/streaming/reference/post/statuses/filter) to listen around a hashtag.

Dependencies
------------
* [Tweepy](https://github.com/tweepy/tweepy)


Love Actually Bot
====================
Compares users' timelines to dialogue from [Love Actually (2003)](http://www.imdb.com/title/tt0314331/) and determines which character's dialogue is the most semantically similar using Latent Semantic Indexing. Uses Google Sheets to store incoming tweets and load responses.

Dependencies
------------
* [Gensim](https://github.com/RaRe-Technologies/gensim)
* [Google API Client Python](https://github.com/google/google-api-python-client)
* [Natural Language Toolkit (NLTK)](https://github.com/nltk/nltk)