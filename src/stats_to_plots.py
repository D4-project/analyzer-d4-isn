import matplotlib.pyplot as plt
import logging
import datetime
import os

import database
from config import COUNT_THRESHOLD, RATIO_THRESHOLD

logging.basicConfig(level=logging.INFO)
log = logging.getLogger('stats_to_plot')

"""
Get stats about the last n days, ending at end timestamp
 - port on which to get stats
 - kind of stats: ALL or ISN-DST
 - end: timestamp of end day OR
        None for yesterday (you do not have enough stats for today, do you?)
 - n: number of days to include (default 30)
"""
def get_last_days(port, kind, end_date=None, n=42):
	date = end_date
	ONE_DAY = datetime.timedelta(days=1)
	# if invalid date, set it to yesterday
	if not hasattr(date, 'day'):
		date = datetime.datetime.today() - ONE_DAY

	days = {}
	for i in range(n):
		str_day = date.strftime('%Y-%m-%d')
		days[str_day] = stats.get_port(date, port, kind)
		date -= ONE_DAY
	return days

def is_interesting(port):
	p_all = get_last_days(port, 'ALL')
	n_all = sum(p_all.values())
	if n_all < COUNT_THRESHOLD:
		return False
	p_isn_dst = get_last_days(port, 'ISN-DST')
	n_isn_dst = sum(p_isn_dst.values())
	if n_isn_dst/n_all < RATIO_THRESHOLD:
		return False
	return True

def get_interesting_ports():
	ports = []
	for p in stats.get_ports():
		if is_interesting(p):
			ports.append(p)
	return ports

def plot(port, img_dir=None):
	# display results
	print('###############################################')
	print('###  Port {}'.format(port))
	print('###############################################')
	# get data
	days_all = get_last_days(port, 'ALL')
	days_isn_dst = get_last_days(port, 'ISN-DST')
	x = sorted(days_all.keys())
	y1 = []
	y2 = []
	for day in x:
		y1.append(days_all[day])
		y2.append(days_isn_dst[day])
		print('\t{}: {}/{}'.format(day, days_isn_dst[day], days_all[day]))

	print()
	#""" plot figure
	fig = plt.figure()
	plt.title('Port {}'.format(port))
	plt.bar(x, y1, label='All')
	plt.bar(x, y2, label='ISN==DST_IP')
	plt.xlabel('Date')
	plt.xticks(rotation='vertical')
	plt.ylabel('TCP SYN packets')
	plt.legend()
	# save or display
	if img_dir:
		plt.savefig('{}/{}.png'.format(img_dir, port), bbox_inches='tight')
	else:
		plt.tight_layout()
		plt.draw()


def get_img_dir():
	path = os.path.dirname(os.path.abspath(__file__))
	# create new directory each day
	today = datetime.datetime.today().strftime('%Y-%m-%d')
	# image directory beside src
	path = os.path.join(path, '..', 'images', today)

	try:
		os.makedirs(path, exist_ok=True)
		return path
	except:
		log.error('error creating directory {}'.format(path))
		return False

def main():
	img_dir = get_img_dir()
	if not img_dir:
		log.error('no good image directory')
		return False

	# TODO add params to set end_date and n
	plt.rcParams.update({'xtick.labelsize': 8})
	for p in get_interesting_ports():
		#print(p)
		plot(p, img_dir)

	# avoid python to exit and keep plot window opened
	#plt.show()


stats = database.Stats_Database()
if __name__ == '__main__':
	main()
