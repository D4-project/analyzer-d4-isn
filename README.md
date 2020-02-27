# analyzer-d4-isn
Analyzer D4 ISN is a D4 analyser to get stats and graphs on TCP SYN packets where
IP_DST==ISN. Those packet are interesting because they are used by smart scanner to
avoid keeping network connection state. This smart scan was first widely used by the
[Mirai](https://en.wikipedia.org/wiki/Mirai_(malware)) botnet to scan for new potential
targets.

# Install
```bash
$ ./install.sh
```
The script will install those dependencies using apt:
- python3
- python3-redis
- screen
- redis-tools

The script will download and compile redis from GitHub in the `./redis` directory and
create the `./db` directory to store the database dump.

The script will finally create the `./image` directory to store created images graphs.

# Launch
```bash
$ ./launch.sh
```

This script will first trigger the installation script to make sure everything is
settled. Then, it will find the first available port to launch the local redis server,
incrementing from port `6379`. You can change this port at
[./launch.sh line 34](https://github.com/D4-project/analyzer-d4-isn/blob/89d58659a4fe6ed37d12246f67f17402bec38bc0/launch.sh#L34).
After making sure redis is ready, the script will load the 2 python workers: `pcap_to_csv`
and `csv_to_stats`.

The workers will automatically create stats inside the local redis database without
creating plots or images.

# Graphs
To get graph images, use the script `./src/stats_to_plot.py`. This will create images
for all _interesting_ ports inside the `./images` directory. You can change thresholds
used to define _interesting_ ports at
[./src/config.py line 13](https://github.com/D4-project/analyzer-d4-isn/blob/89d58659a4fe6ed37d12246f67f17402bec38bc0/src/config.py#L13).

To automatically create graphs everyday, you can create a cronjob with this script.
Example for everyday at 3am:
```
0 3 * * * /usr/bin/python3 /PATH/TO/src/stats_to_plot.py
```

# First launch
If your D4 server is in production for a long time and you create a new queue for this
analyser, it start empty and you will not get past data. You then should wait 30 days
to get 30-days stats in the database and get nice graphs. If you want to get stats about
the past, you can manually add PCAP to the processing queue.

| :warning: A misuse of this tool can make PCAP files to be processed twice and create wrong stats! |
| --- |

This tool will effectively check that PCAP files already in the queue will NOT be added
twice. Though it has no knownledge about PCAP files already poped from the queue. To
avoid data duplication, it is advised to run this tool when your database is empty and
workers are stopped. To empty your database, you need to stop the redis server (CTRL^C)
and delete the `./db/dump.rdb` file.

To add pcap files inside a folder (including in subfolders), run this command:
```bash
$ python3 ./src/add_files.py DIRECTORY
```

Then you can start the workers again with `./launch.sh`.
