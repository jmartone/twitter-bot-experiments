import tweepy
from queue import Queue
import threading

class TwitterBot(object):

	def threaded(fn):
	    def wrapper(*args, **kwargs):
	        thread = threading.Thread(target=fn, args=args, kwargs=kwargs)
	        thread.setDaemon(True)
	        thread.start()
	        return thread
	    return wrapper

	def __init__(self, CREDS):
		# intialize twitter API
		self.twitterAuth = tweepy.OAuthHandler(CREDS['CONSUMER_KEY'], CREDS['CONSUMER_SECRET'])
		self.twitterAuth.set_access_token(CREDS['ACCESS_TOKEN'], CREDS['ACCESS_TOKEN_SECRET'])

	@threaded
	def handleQueue():
	    while True:
	        status = q.get()
	        self.handleStatus(status)
	        q.task_done()

	@threaded
	def _startThreaded(self):
		self._start()

    def _start(self):

    	# set up listener class
		class BotListener(tweepy.StreamListener):
	    	def on_status(self, status):
	        	q.put(status)

		    def on_error(self, status_code):
		        if status_code == 420:
		            print("Rate limited!")
		            return False

     	# TODO: HANDLE DISCONNECT ERRORS
		while True:
		    try:
		        listener = BotListener()
		        stream = tweepy.Stream(auth = twitterAuth, listener=listener)
		        stream.filter(track = filters)
		    except KeyboardInterrupt:
		        # Or however you want to exit this loop
		        stream.disconnect()
		        break
	
	def start(self, filters, handleStatus, threaded = False):
		self.handleStatus = handleStatus
		q = Queue()
		self.handleQueue()
		if (threaded):
			self._startThreaded()
		else:
			self._start()