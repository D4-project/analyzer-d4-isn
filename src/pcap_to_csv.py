import subprocess
import logging
import os

import database

logging.basicConfig(level=logging.INFO)
log = logging.getLogger('pcap_to_csv')


def has_tshark():
	try:
		result = subprocess.check_output(['tshark', '--version'], stderr=subprocess.STDOUT)
		return True
	except:
		return False


def pcap_to_csv_lines(pcap_file, filters, fields, options):
	if not os.path.isfile(pcap_file):
		log.error('file "{}" does not exists'.format(pcap_file))
		return False
	if not has_tshark():
		log.error('tshark was not found, did you install it?')
		return False
	cmd = [
		'tshark',
		'-n', # no reverse lookup
		'-r', pcap_file,
		'-2', '-R', filters, # filter extracted packets
		'-T', 'fields', # CSV output
	]
	for f in fields:
		cmd.append('-e')
		cmd.append(f)
	for o in options:
		cmd.append('-o')
		cmd.append(o)
	try:
		result = subprocess.check_output(cmd, stderr=subprocess.STDOUT, universal_newlines=True)
	except:
		log.error('error while executing tshark command')
		return False
	return ''.join(result).split("\n")


def tcp_syn_lines(pcap_file):
	filters = 'not icmp and tcp and tcp.flags.syn == 1 and tcp.flags.ack == 0'
	fields = ['frame.time_epoch', 'ip.dst', 'tcp.dstport', 'tcp.seq']
	options = ['tcp.relative_sequence_numbers:0']
	return pcap_to_csv_lines(pcap_file, filters, fields, options)

def main():
	while True:
		log.info('waiting for a pcap file to process')
		pcap_file = d4.pop()
		log.info('parsing file "{}"'.format(pcap_file))
		lines = tcp_syn_lines(pcap_file)
		if not lines:
			log.error('error parsing file "{}"'.format(pcap_file))
			continue
		for l in lines:
			csv.push(l)

if __name__ == '__main__':
	d4 = database.D4_PCAP_Queue()
	csv = database.LOCAL_CSV_Queue()
	main()
