#!/usr/bin/env python

"""Connect to uWSGI stats socket and wait until all
workers are in 'idle' state.

It will return code 0 only if all workers are idle
"""

from __future__ import print_function

import argparse
import json
import os
import socket
import sys
import time

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('socket',
                   help='filename of uWSGI UNIX socket')
parser.add_argument('--timeout', '-t', type=int, metavar='N', default=30,
                   help='timeout in seconds')
args = parser.parse_args()


def load_stats(socket_name):
    """connect to stats socket and read the data"""

    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        sock.connect(socket_name)
    except socket.error as e:
        print('sock.connect() on {}: '.format(socket_name), end='', file=sys.stderr)
        raise
    js_str = ''
    while True:
        data = sock.recv(4096)
        if len(data) < 1:
            break
        js_str += data.decode('utf8')
    js = json.loads(js_str)

    return js


def get_worker_status_counts(js):
    """sum worker status counts by status type"""

    if 'workers' not in js:
        raise ValueError('Expecting JSON with "workers" key')

    status_counts = { 'total': 0, }
    for w in js['workers']:
        status = w.get('status', 'unknown')
        status_counts.setdefault(status, 0)
        status_counts[status] += 1
        status_counts['total'] += 1

    return status_counts


def main():
    """loop until all workers are idle or timeout reached"""

    wait_till = time.time() + args.timeout
    while True:
        js = load_stats(args.socket)

        counts = get_worker_status_counts(js)

        if counts.get('idle', 0) == counts['total']:
            print('All workers are idle')
            break

        print(' '.join('{}: {}'.format(k, v) for k, v in sorted(counts.items())))

        if time.time() >= wait_till:
            print('Timeout ({}s) reached.'.format(args.timeout), file=sys.stderr)
            sys.exit(2)

        time.sleep(1)

    sys.exit(0)

try:
    main()
except KeyboardInterrupt:
    pass
except (ValueError, socket.error) as e:
    print(e, file=sys.stderr)
    sys.exit(1)
