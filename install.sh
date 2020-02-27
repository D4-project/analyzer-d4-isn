
DIR=$(dirname "${BASH_SOURCE[0]}")
DIR=$(realpath "$DIR")


# check and install screen and redis-cli
while
	dpkg -l python3 python3-redis screen redis-tools 2> /dev/null > /dev/null
	[ $? != 0 ]
do
	echo 'Installing dependencies'
	sudo apt-get install python3 python3-redis screen redis-tools -y
done


# image path
mkdir -p "$DIR/images"


# redis
mkdir -p "$DIR/db"
if [ ! -d "$DIR/redis" ]
then
	echo 'Downloading Redis from GitHub'
	git clone https://github.com/antirez/redis.git "$DIR/redis"
	pushd "$DIR/redis"
	git checkout 5.0
	echo 'Compiling Redis'
	make
	echo 'Redis successfully installed'
	popd
else
	echo 'Redis already installed'
fi
