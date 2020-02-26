#!/bin/bash

DIR=$(dirname "${BASH_SOURCE[0]}")
DIR=$(realpath "$DIR")



# install first
. "$DIR/install.sh"



# ip from hex 0100007F to ascii 127.0.0.1
function ip_h2a() {
	if [ "$1" = '' ]
	then
		echo 'no ip'
		return 1
	fi
	IP=$(echo "ibase=16;$1" | bc)
	while
		echo -n $(echo "$IP%256" | bc)
		IP=$(echo "$IP/256" | bc)
		[ $IP -ne 0 ]
	do
		echo -n '.'
	done
	echo ''
}



echo "looking for one free port from $LOCAL_REDIS_PORT to bind local redis"
LOCAL_REDIS_PORT=6379
while
	HEX_PORT=$(echo "ibase=10;obase=16;$LOCAL_REDIS_PORT" | bc)
	LISTENING=$(cat /proc/net/tcp | sed 's/\s\s*/ /g' | grep ' 0A ')
	IP=$(echo "$LISTENING" | cut -d ' ' -f 3 | grep "$HEX_PORT" | cut -d ':' -f 1)
	[ "$IP" != '' ]
do
	echo "port $LOCAL_REDIS_PORT already bound on $(ip_h2a $IP)"
	LOCAL_REDIS_PORT=$(echo "$LOCAL_REDIS_PORT+1" | bc)
done

# set redis port in config
echo "set redis local port to $LOCAL_REDIS_PORT"
sed -i "s/^LOCAL_REDIS_PORT=[0-9]*/LOCAL_REDIS_PORT=$LOCAL_REDIS_PORT/g" "$DIR/src/config.py"
sed -i "s/^port [0-9]*/port $LOCAL_REDIS_PORT/g" "$DIR/local-redis.conf"
sed -i "s/^pidfile \/var\/run\/redis_[0-9]*.pid/pidfile \/var\/run\/redis_$LOCAL_REDIS_PORT.pid/g" "$DIR/local-redis.conf"



# start screen
SCREEN_NAME='analyzer-d4-isn'
screen -dmS "$SCREEN_NAME"
sleep 1



# redis
echo "Starting redis-server in screen $SCREEN_NAME, tab redis-server"
REDIS_CMD="$DIR/redis/src/redis-server $DIR/local-redis.conf"
screen -S "$SCREEN_NAME" -X screen -t "redis-server" bash -c "($REDIS_CMD); read x;"

# wait for redis to load database before starting workers
echo -n 'Waiting for Redis to load database .'
while
	redis-cli -h '127.0.0.1' -p "$LOCAL_REDIS_PORT" PING 2> /dev/null > /dev/null
	[ $? != 0 ]
do
	echo -n '.'
	sleep 1
done
echo ''
echo 'Redis database loaded'



PYTHON_WORKERS=('pcap_to_csv' 'csv_to_stats')
for FILE in ${PYTHON_WORKERS[@]}
do
	CMD="python3 $DIR/src/$FILE.py"
	NAME=$(basename "$CMD")
	echo "Starting $NAME in screen $SCREEN_NAME, tab $NAME"
	screen -S "$SCREEN_NAME" -X screen -t "$NAME" bash -c "($CMD); read x;"
done


echo 'Everything started, please look at the screens for eventual errors'
