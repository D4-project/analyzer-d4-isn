import logging
import datetime

import database

logging.basicConfig(level=logging.INFO)
log = logging.getLogger('csv_to_stats')


def ip_to_int(ip):
	parts = ip.split('.')
	i = 0
	for p in parts:
		i *= 256
		i += int(p)
	return i


def parse_line(epoch, dst_ip, dst_port, tcp_isn):
	ts = int(epoch.split('.')[0])
	date = datetime.datetime.fromtimestamp(ts)
	dst_port = int(dst_port)
	tcp_isn = int(tcp_isn)

	stats.add_port_all(date, dst_port)
	try:
		if ip_to_int(dst_ip) == tcp_isn:
			stats.add_port_isn_dst(date, dst_port)
	except ValueError:
		log.error('ValueError on string "{},{},{},{}"'.format(epoch, dst_ip, dst_port, tcp_isn))


def main():
	while True:
		log.info('waiting for a CSV line to process')
		csv_line = csv.pop()
		log.info('processing line: {}'.format(csv_line))
		# some lines are empty
		if not csv_line:
			continue
		args = csv_line.split('\t')
		if len(args) != 4:
			log.error('Not 4 splitted in {}'.format(csv_line))
		else:
			parse_line(*args)


if __name__ == '__main__':
	csv = database.LOCAL_CSV_Queue()
	stats = database.Stats_Database()
	main()
