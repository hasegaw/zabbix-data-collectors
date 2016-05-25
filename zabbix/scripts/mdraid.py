#! /usr/bin/env python
#
# The MIT License (MIT)
#
# Copyright (c) 2016 Takeshi HASEGAWA <hasegaw@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import argparse
import json
import pprint
import re
from subprocess import Popen, PIPE
import sys


def read_proc_mdstat(cmd=None):
    cmd = cmd or 'cat /proc/mdstat'

    p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, close_fds=True)
    (child_stdout, child_stdin) = (p.stdout, p.stdin)
    output = child_stdout.read()

    if isinstance(output, bytes):
        output = output.decode('utf-8')

    lines = output.split('\n')
    return lines


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-C', type=str, dest='source_command')
    parser.add_argument('device', type=str)
    parser.add_argument('key', type=str, choices=(
        'total', 'status', 'active', 'inactive', 'all'))
    return parser.parse_args()


def parse_lines(lines):
    entries = []

    current = {}
    for line in lines:
        m = re.match(r'^md(?P<md_index>\d+) : (?P<status>\S+)', line)
        if m:
            current = {
                'dev': 'md%s' % m.group('md_index'),
                'md_index': int(m.group('md_index')),
                'status': m.group('status'),
            }
            continue

        elif 'md_index' in current:
            m = re.match(
                r'^\s+(?P<blocks>\d+) blocks.*\[(?P<member_status>\S+)]$', line)

            if not m:
                current = {}
                continue

            current['total'] = len(m.group('member_status'))
            current['active'] = 0
            current['inactive'] = 0
            current['blocks'] = int(m.group('blocks'))

            for member in m.group('member_status'):
                if member == 'U':
                    current['active'] = current['active'] + 1

                if member == '_':
                    current['inactive'] = current['inactive'] + 1

            entries.append(current)
            current = {}

    return entries


def main():
    args = get_args()

    lines = read_proc_mdstat(cmd=args.source_command)

    entries = parse_lines(lines)
    entry = [e for e in entries if e['dev'] == args.device]

    assert len(entry) <= 1

    if len(entry) == 0:
        sys.exit(0)

    entry = entry.pop(0)

    if args.key == 'all':
        pprint.pprint(entry)

    else:
        print(entry[args.key])


if __name__ == '__main__':
    main()
