#!/usr/bin/python

from threading import Thread
import progressbar
import argparse
import sys
import logging
import os.path
import math
import urllib2
# http://services.wakegov.com/realestate/Account.asp?id=0409178

threads = []
running = True
progressCount = 0

parser = argparse.ArgumentParser(description='My description')
parser.add_argument('min', metavar='0', type=int, help='minimum range value, not inclusive')
parser.add_argument('max', metavar='400000', type=int, help='maximum range value, inclusive')
parser.add_argument('--output', dest='output', default='data', help='output directory')
parser.add_argument('--threads', dest='threads', default=10, help='number of threads', type=int)
parser.add_argument('--logdir', dest='logdir', default='./', help='directory used for logging')

args = parser.parse_args()

def create_thread(id_start, id_end):
    logging.debug('create_thread(%s, %s)', id_start, id_end)
    t = Thread(target=do_scrape, args=(id_start, id_end, ) )
    threads.append(t)

# Define a function for the thread
def do_scrape(id_start, id_end):
    global progressCount 
    logging.debug('do_scrape(%s, %s)', id_start, id_end)
    # end of range is not inclusive
    for x in range(int(id_start), int(id_end) + 1):
        if not running:
            break
        filename = "{}/{}".format(args.output, x)
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
        progressCount += 1

def do_progress():
    progressTotal = 100
    progressCurrent = (progressTotal * progressCount / (thread_ranges[1] - thread_ranges[0]))
    sys.stdout.write("\r[" + "=" * progressCurrent + " " * (progressTotal - progressCurrent) + "] " + str(int(100 * progressCurrent / progressTotal)) + "%")
    sys.stdout.flush()

# create output dir if it doesn't exist
if not os.path.exists(args.output):
    os.makedirs(args.output)

log_dir = args.logdir
if not os.path.exists(log_dir):
    os.makedirs(log_dir)


# setup logging
logging.basicConfig(format='time="%(asctime)s" level="%(levelname)s" message="%(message)s"', level=logging.DEBUG, filename='{}/scrape.log'.format(log_dir))
logging.info('START')

# setup range
# first index is not inclusive
#thread_ranges = [args['min'], args['max']]
thread_ranges = [args.min, args.max]

print "Using ID range: [{}, {}]".format(thread_ranges[0], thread_ranges[1])


thread_count = args.threads
total = thread_ranges[1] - thread_ranges[0]

# if thread count is less than 1, reset to 1
if thread_count < 1:
    thread_count = 1

# if thread count is bigger than total, reset thread count
if thread_count > total:
    thread_count = total

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
            do_progress()
            x.join(0.1) # 0.1 seconds
            if not x.is_alive():
                logging.info('THREAD CLOSED: %s', x.ident)
                threads.remove(x)
    except KeyboardInterrupt:
        print "Program will exist in a moment..."
        running = False
        break

progressCount = thread_ranges[1] - thread_ranges[0]
do_progress()
sys.stdout.write('\n')

logging.info('END')
