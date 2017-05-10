# uses python3 because it handles unicode better
import os
import numpy
import pandas as pd
import requests
import unicodedata
import re
import tweepy
import json
from TwitterBot import TwitterBot
from apiclient.discovery import build
from time import sleep
from thread_wrapper import threaded
from queue import Queue
from gensim import corpora, models, similarities
from nltk import stem
from nltk.corpus import stopwords

# VARIABLES
# load stopwords and stemmer for NLP
stops = stopwords.words('english')
snowball = stem.snowball.EnglishStemmer()
# intialize Google Sheets API
GOOGLE_APPLICATION_CREDENTIALS = 'google_sheets.json'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.abspath(GOOGLE_APPLICATION_CREDENTIALS)
sheetsAPI = build('sheets', 'v4')
#initialize the Twitter API
with open('twitter_creds.json', 'r') as twitter_creds_json:
	creds = json.loads(twitter_creds_json.read())
twitterAuth = tweepy.OAuthHandler(creds['CONSUMER_KEY'], creds['CONSUMER_SECRET'])
twitterAuth.set_access_token(creds['ACCESS_TOKEN'], creds['ACCESS_TOKEN_SECRET'])
# initialize Google Sheets variables
spreadsheetId = '1ZFMmbL9qmCFBdxtP4J1CRZbWDCC8nyzfeHaoVptdrV0'
sheetId_ALL = 610325669
sheetName_PRIZES = 'CHAR'
# set hashtag to track
hashtag = "loveactuallyme"
# load the model
dictionary = corpora.Dictionary.load('love_actually/love_actually.dict')
corpus = corpora.MmCorpus('love_actually/love_actually.mm')
index = similarities.MatrixSimilarity.load('love_actually/love_actually.index')
lsi = models.LsiModel(corpus, id2word=dictionary, num_topics=300)
# extract prize settings from sheet
result = sheetsAPI.spreadsheets().values().get(spreadsheetId = spreadsheetId, range = sheetName_PRIZES + '!A1:C100').execute()
values = result.get('values', [])
prizes = pd.DataFrame(values[1:], columns = values[0])
prizes.index = prizes['id']
# set initial media_id to False
prizes.loc[:, 'media_id'] = False

# uploads media one at a time refreshing after the expirey time ad infinitum
@threaded
def upload_media(i, url):
	while True:
		prizes.loc[i, 'media_id'] = False
		print("Re-uploading " + url)
		filename = str(hash(url)) + '.jpg'
		try:
			request = requests.get(url, stream=True)
		except requests.exceptions.ConnectionError:
			print("Connection refused, trying again in 5s")
			sleep(5)
			continue
		if request.status_code == 200:
			with open(filename, 'wb') as image:
				for chunk in request:
					image.write(chunk)
			while True:
				res = ''
				try:
					res = twitterAPI.media_upload(filename)
					break
				except tweepy.TweepError:
					print("Upload failed, trying again in 5s")
					sleep(5)
			os.remove(filename)
			prizes.loc[i, 'media_id'] = res['media_id_string']
			print("Uploaded " + url)
			sleep(res['expires_after_secs'])
		else:
			print("Error downloading " + url)

for i, prize in prizes.iterrows():
	upload_media(i, prize['asset'])

# Google Sheets does not have a native insert row API call, so I built my own
def insertRow(spreadsheetId, sheetId, startRow, valuesArray):
	# convert multidimensional array to json
	values = [
		[
			{
				'userEnteredValue': {
					'stringValue': value
				}
			} for value in row
		] for row in valuesArray
	]
	# create the requests, first inserting rows, then adding data in the empty rows
	requests = {
		'requests': [
			{
				"insertDimension": {
					"range": {
						'sheetId': sheetId,
						"dimension": "ROWS",
						"startIndex": startRow,
						"endIndex": startRow + len(values)
					}
				}
			},
			{
				'updateCells': {
					'rows': [
						{
							'values': values
						}
					],
					'fields': '*',
					'start': {
						'sheetId': sheetId,
						"rowIndex": startRow,
						"columnIndex": 0
					}
				}
			}
		]
	}
	sheetsAPI.spreadsheets().batchUpdate(spreadsheetId = spreadsheetId, body = requests).execute()

# uses regex to remove punctuation
def remove_punctuation(text):
	return re.sub(r"\\p{P}+", "", text)

# tokenize and stem documents for NLP
def tokenize_and_stem(document):
	# add a space after elipses
	document = re.sub(r"\\.\\.\\.", "... ", document)
	# remove punctuation
	document = remove_punctuation(document)
	# lowercase
	document = document.lower()
	# remove stop words
	tokens = [word for word in document.split() if word not in stops]
	# stem
	return [snowball.stem(word) for word in tokens]

# compare timeline to model
def handleStatus(status):
	# ignore RTs
	if (hasattr(status, 'retweeted_status')):
		return
	timeline = []
	timelineDocument = ''
	# collect the user's timeline
	while True:
		try:
			timeline = twitterAPI.user_timeline(status.user.screen_name, count = 200, tweet_mode = 'extended')
			if (len(timeline) > 0):
				break
			else:
				print("User only has 0 tweets")
				return
		except tweepy.TweepError as e:
			if (type(e.message[0]) == dict) and ('code' in e.message[0]):
				# Sorry, that page does not exist
				if (e.message[0]['code'] == 34):
					print('User not found, cannot collect timeline')
					return
				# Rate limit exceeded
				elif (e.message[0]['code'] == 88):
					print('Timeline rate limit hit, waiting 15 minutes then trying again')
					sleep(60*60*15+1)
			# User is private
			elif (str(e).lower().find('not authorized') >= 0):
				print('User is private, cannot collect timeline')
				return
			# User is not found
			elif (str(e).lower().find('does not exist') >= 0):
				print('User does not exist')
				return
			# other generic error
			else:
				print('Error, trying again')

	# add each tweet to their document, excluding RTs
	for tweet in timeline:
		if tweet.get('retweeted_status', False):
			continue
		timelineDocument += tweet['full_text'] + " "
	# convert their document to a bag of words
	vec_bow = dictionary.doc2bow(tokenize_and_stem(timelineDocument))
	# project the vector into the LSI
	vec_lsi = lsi[vec_bow]
	# use the LSI index to establish a similarity
	sims = index[vec_lsi]
	# create a temporary version of the prizes dataframe to determine results
	prize_winners = prizes
	prize_winners.loc[:, 'sim'] = sims
	character = prize_winners.loc[prize_winners['sim'].idxmax(), 'character']
	asset = prize_winners.loc[prize_winners['sim'].idxmax(), 'media_id']
	sim = prize_winners.loc[prize_winners['sim'].idxmax(), 'sim']
	# send a reply with the result
	reply = twitterAPI.update_status(
			'@' + status.user.screen_name + ' ' + character,
			in_reply_to_status_id = status.id,
			media_ids = [asset]
		)
	# create a list of data to insert into the sheet
	row = [
		'http://www.twitter.com/' + status.user.screen_name + '/status/' + status.id_str,
		status.text,
		status.created_at.strftime('%m/%d/%Y'),
		status.created_at.strftime('%H:%M'),
		character,
		str(sim)
	]
	# write data to sheet
	insertRow(spreadsheetId, sheetId_ALL, 1, [row])

if __name__ == '__main__':
	twitterAPI = tweepy.API(twitterAuth, parser=tweepy.parsers.JSONParser())
	bot = TwitterBot(filters = '#' + hashtag, twitterAuth = twitterAuth, callback = handleStatus).start()