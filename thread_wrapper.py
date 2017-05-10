import threading

def threaded(fn):
	def wrapper(*args, **kwargs):
		thread = threading.Thread(target=fn, args=args, kwargs=kwargs)
		thread.setDaemon(True)
		thread.start()
		return thread
	return wrapper