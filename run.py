import sys

def do_work():
	""" Function to handle command line usage"""
	args = sys.argv
	args = args[1:] # First element of args is the file name
    

if __name__ == '__main__':
	do_work()