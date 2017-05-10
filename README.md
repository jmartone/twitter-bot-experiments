# twitter-bot-experiments

A basic Twitter bot that employs the [Twitter Streaming API](https://dev.twitter.com/streaming/reference/post/statuses/filter) to listen around a hashtag.

Dependencies
------------
* [Tweepy](https://github.com/tweepy/tweepy)


Love Actually Bot
====================
Compares users' timelines to dialogue from [Love Actually (2003)](http://www.imdb.com/title/tt0314331/) and determines which character's dialogue is the most semantically similar using Latent Semantic Indexing. Uses Google Sheets to store incoming tweets and load responses.

Requires authentication information in two JSON files `google_sheets.json` and `twitter_creds.json` with the following formats:

__google_sheets.json__
NOTE: ensure that your sheet is shared with your service account, credentials can be found on [Google's Cloud Platform](https://console.cloud.google.com/apis/credentials)

	{
		"type": "service_account",
		"project_id": "[PROJECT_ID]",
		"private_key_id": "[PRIVATE_KEY_ID]",
		"private_key": "[PRIVATE_KEY]",
		"client_email": "[CLIENT_EMAIL]",
		"client_id": "[CLIENT_ID",
		"auth_uri": "[auth_uri]",
		"token_uri": "[token_uri]",
		"auth_provider_x509_cert_url": "[auth_provider_x509_cert_url]",
		"client_x509_cert_url": "[client_x509_cert_url]"
	}
__twitter_creds.json__

	{
	    "CONSUMER_KEY": "[CONSUMER_KEY",
	    "CONSUMER_SECRET": "[CONSUMER_SECRET]",
	    "ACCESS_TOKEN": "[ACCESS_TOKEN]",
	    "ACCESS_TOKEN_SECRET": "[ACCESS_TOKEN_SECRET]"
	}

Dependencies
------------
* [Gensim](https://github.com/RaRe-Technologies/gensim)
* [Google API Client Python](https://github.com/google/google-api-python-client)
* [Natural Language Toolkit (NLTK)](https://github.com/nltk/nltk)