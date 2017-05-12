import tweepy
from queue import Queue
from thread_wrapper import threaded
import os
import joblib

class TwitterBot(object):

	def __init__(self, filters = None, callback = None, creds = None, twitterAuth = None, enableCache = True):
		if (twitterAuth):
			self.twitterAuth = twitterAuth
		else:
			# intialize twitter API
			self.twitterAuth = tweepy.OAuthHandler(creds['CONSUMER_KEY'], creds['CONSUMER_SECRET'])
			self.twitterAuth.set_access_token(creds['ACCESS_TOKEN'], creds['ACCESS_TOKEN_SECRET'])
		# set the filters
		if (type(filters) == list):
			self.filters = filters
		else:
			self.filters = [filters]
		self.callback = callback
		self.loadQueue = loadQueue

	@threaded
	def _startThreaded(self):
		self._start()

	def _start(self):
		# set up listener class
		class BotListener(tweepy.StreamListener):

			def __init__(self, callback, enableCache = True, cacheDir = 'cache', cacheFile = 'queue.cache', *args, **kwargs):
				self.q = Queue()
				self.enableCache = enableCache
				if (self.enableCache):
					self.cacheDir = cacheDir
					self.cacheFile = cacheFile
					# create the cacheDir directory if it doesn't exist
					if not os.path.exists(self.cacheDir):
						os.makedirs(self.cacheDir)
					# load the cached queue if it exists
					if (os.path.isfile(self.cacheDir + self.cacheFile)):
						qList = joblib.load(self.cacheDir + self.cacheFile)
						[self.q.put(item) for item in qList]
				self.handleQueue()
				self.callback = callback
				tweepy.StreamListener.__init__(self)

			@threaded
			def handleQueue(self):
				while True:
					if (self.enableCache)
						# convert the queue to a list and dump it to the cache
						joblib.dump(list(self.q.queue), self.cacheDir + self.cacheFile)
					status = self.q.get()
					self.callback(status)
					self.q.task_done()

			def on_status(self, status):
				self.q.put(status)

			def on_error(self, status_code):
				if status_code == 420:
					print("Rate limited!")
					return False

		# TODO: HANDLE DISCONNECT ERRORS
		while True:
			try:
				listener = BotListener(self.callback, enableCache = self.enableCache)
				stream = tweepy.Stream(auth = self.twitterAuth, listener = listener)
				stream.filter(track = self.filters)
			except KeyboardInterrupt:
				# Or however you want to exit this loop
				stream.disconnect()
				break
			except:
				print("Stream disconnected, reconnecting")
				continue
	
	def start(self, threaded = False):
		if (threaded):
			self._startThreaded()
		else:
			self._start()