import subprocess
import os
import logging

import database

"""
Helper to add files to D4 server queue
"""
logging.basicConfig(level=logging.INFO)
log = logging.getLogger('add_files')

def get_files(directory):
	cmd = ['find', directory, '-type', 'f', '-name', '*.cap*']
	try:
		result = subprocess.check_output(cmd, stderr=subprocess.STDOUT, universal_newlines=True)
	except:
		log.error('error while executing find command')
		return None

	files = ''.join(result).splitlines()
	return [os.path.abspath(f) for f in files]


def array_to_dic(array):
	return dict(zip(array, [True for e in array]))


def main():
	import sys

	if len(sys.argv) < 2:
		exit('usage: python3 '+sys.argv[0]+' DIRECTORY [LIMIT]')
	d = sys.argv[1]
	if not os.path.isdir(d):
		exit('"{}" is not a valid directory'.format(d))

	limit = len(sys.argv) > 2
	if limit:
		n = int(sys.argv[2])

	# get fs files before looking into queue
	files = get_files(d)
	if type(files) != list:
		exit('error listing files')
	# look at the queue now
	existings = array_to_dic(d4.all())

	for f in files:
		# skip already added files
		if f in existings:
			log.info('skipping existing file {}'.format(f))
			continue
		if limit and n < 1:
			break
		d4.push(f)
		log.info('add file "{}"'.format(f))
		if limit:
			n -= 1

if __name__ == '__main__':
	d4 = database.D4_PCAP_Queue()
	main()
