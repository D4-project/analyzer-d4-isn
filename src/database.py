import redis

from config import *


class Database:
	def __init__(self, host, port, db):
		self.db = redis.Redis(host=host, port=port, db=db)


"""
FIFO Queue using Redis lists
"""
class Queue(Database):
	def __init__(self, host, port, db, name):
		super().__init__(host, port, db)
		self.name = name
	# return index
	def push(self, elmt):
		return self.db.lpush(self.name, elmt)
	# return decoded string value
	def pop(self):
		(name, value) = self.db.brpop(self.name)
		return value.decode('UTF-8')
	def all(self):
		decoded = []
		encoded = self.db.lrange(self.name, 0, int(1e18))
		return [e.decode('UTF-8') for e in encoded]


class D4_PCAP_Queue(Queue):
	def __init__(self):
		super().__init__(
			D4_REDIS_HOST,
			D4_REDIS_PORT,
			D4_REDIS_DB,
			'analyzer:1:{}'.format(D4_UUID)
		)


class LOCAL_CSV_Queue(Queue):
	def __init__(self):
		super().__init__(
			LOCAL_REDIS_HOST,
			LOCAL_REDIS_PORT,
			LOCAL_CSV_DB,
			'CSV-QUEUE'
		)


class Stats_Database(Database):
	def __init__(self):
		super().__init__(
			LOCAL_REDIS_HOST,
			LOCAL_REDIS_PORT,
			LOCAL_STATS_DB
		)
		self.PORT_FORMAT = 'TCP-ISN-IP_{}_{}_{}'

	def add_port_all(self, date, port):
		return self.add_port(date, port, 'ALL')

	def add_port_isn_dst(self, date, port):
		return self.add_port(date, port, 'ISN-DST')

	def add_port(self, date, port, kind):
		# TODO maybe add expire depending on wanted retention?
		day = date.strftime('%Y-%m-%d')
		key = self.PORT_FORMAT.format(day, port, kind)
		return self.db.incr(key)

	def get_port_all(self, date, port):
		return self.get_port(date, port, 'ALL')

	def get_port_isn_dst(self, date, port):
		return self.get_port(date, port, 'ISN-DST')

	def get_port(self, date, port, kind):
		day = date.strftime('%Y-%m-%d')
		key = self.PORT_FORMAT.format(day, port, kind)
		val = self.db.get(key)
		if val:
			return int(val)
		return 0

