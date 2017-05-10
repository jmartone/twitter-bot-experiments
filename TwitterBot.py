import tweepy
from queue import Queue
from thread_wrapper import threaded

class TwitterBot(object):

	def __init__(self, filters = None, callback = None, creds = None, twitterAuth = None):
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

	@threaded
	def _startThreaded(self):
		self._start()

	def _start(self):
		# set up listener class
		class BotListener(tweepy.StreamListener):

			def __init__(self, callback, *args, **kwargs):
				self.q = Queue()
				self.handleQueue()
				self.callback = callback
				tweepy.StreamListener.__init__(self)

			@threaded
			def handleQueue(self):
				while True:
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
				listener = BotListener(self.callback)
				stream = tweepy.Stream(auth = self.twitterAuth, listener = listener)
				stream.filter(track = self.filters)
			except KeyboardInterrupt:
				# Or however you want to exit this loop
				stream.disconnect()
				break
	
	def start(self, threaded = False):
		if (threaded):
			self._startThreaded()
		else:
			self._start()