#!/usr/bin/python

from threading import Thread
import sys
import logging
import os.path
import math
import urllib2
# http://services.wakegov.com/realestate/Account.asp?id=0409178

threads = []
running = True

def create_thread(id_start, id_end):
    logging.debug('create_thread(%s, %s)', id_start, id_end)
    t = Thread(target=do_scrape, args=(id_start, id_end, ) )
    threads.append(t)

# Define a function for the thread
def do_scrape(id_start, id_end):
    logging.debug('do_scrape(%s, %s)', id_start, id_end)
    # end of range is not inclusive
    for x in range(int(id_start), int(id_end) + 1):
        if not running:
            break
        filename = "data/{}".format(x)
        if os.path.isfile(filename):
            logging.debug('%s: data exists', x)
        else:
            logging.debug('%s: start scraping', x)
            try:
                u =  urllib2.urlopen("http://services.wakegov.com/realestate/Account.asp?id={0:07d}".format(x))
                f = open(filename, "w")
                f.write(u.read())
                u.close()
                f.close()
                logging.debug('%s: end scraping', x)
            except urllib2.HTTPError as e:
                logging.error('%s: HTTPError - [%s] %s', x, e.code, e.reason)
            except urllib2.URLError as e:
                logging.error('%s: URLError - %s', x, e.reason)

# create data and target dir if it doesn't exist
if not os.path.exists("target"):
    os.makedirs("target")

if not os.path.exists("data"):
    os.makedirs("data")

# setup logging
logging.basicConfig(format='time="%(asctime)s" level="%(levelname)s" message="%(message)s"', level=logging.DEBUG, filename='target/scrape.log')
logging.info('START')

# setup range
# note, argv[0] is program name
# first index is not inclusive
print sys.argv
if len(sys.argv) == 3:
    thread_ranges = [int(sys.argv[1]), int(sys.argv[2])]
else:
    thread_ranges = [0, 400000]

print "Using ID range: [{}, {}]".format(thread_ranges[0], thread_ranges[1])

thread_count = 10
total = thread_ranges[1] - thread_ranges[0]
thread_range = math.floor(total / thread_count)

for x in range(thread_count):
    offset = thread_ranges[0] + x * thread_range
    create_thread(offset + 1, offset + thread_range, )

max_range = thread_ranges[0] + thread_count * thread_range
if max_range < thread_ranges[1]:
    create_thread(max_range + 1, thread_ranges[1])

[x.start() for x in threads]

while len(threads) > 0:
    try:
        for x in threads:
            x.join(100)
            if not x.is_alive():
                logging.info('THREAD CLOSED: %s', x.ident)
                threads.remove(x)
    except KeyboardInterrupt:
        print "Program will exist in a moment..."
        running = False
        break

logging.info('END')
