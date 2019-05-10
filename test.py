import traceback
import sys

def test():
	try:
		raise Exception('Oh no!')
	except Exception as e:
		exc = sys.exc_info()
		s = traceback.format_exception(exc[0], exc[1], exc[2])
		print(s)

test()
