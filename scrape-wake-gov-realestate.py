#!/usr/bin/python

from threading import Thread
import logging
import os.path
import math
import urllib2
# http://services.wakegov.com/realestate/Account.asp?id=0409178

threads = []

def create_thread(id_start, id_end):
    logging.debug('Thread started: %s, %s', id_start, id_end)
    t = Thread(target=do_scrape, args=(id_start, id_end, ) )
    threads.append(t)

# Define a function for the thread
def do_scrape(id_start, id_end):
    #print "scrape[{}, {}]".format(int(id_start), int(id_end))
    for x in range(int(id_start), int(id_end)):
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

logging.basicConfig(format='time="%(asctime)s" level="%(levelname)s" message="%(message)s"', level=logging.DEBUG, filename='scrape.log')
logging.info('START')

thread_count = 100
# first index is not inclusive
#thread_ranges = [0, 409178]
thread_ranges = [100000, 200000]
total = thread_ranges[1] - thread_ranges[0]
thread_range = math.floor(total / thread_count)

for x in range(thread_count):
    offset = thread_ranges[0] + x * thread_range
    create_thread(offset + 1, offset + thread_range, )

max_range = thread_ranges[0] + thread_count * thread_range
if max_range < thread_ranges[1]:
    create_thread(max_range + 1, thread_ranges[1])

[x.start() for x in threads]

for x in threads:
    x.join()
    logging.info('THREAD CLOSED: %s', x.ident)

logging.info('END')
