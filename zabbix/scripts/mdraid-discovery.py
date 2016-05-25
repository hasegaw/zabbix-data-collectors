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

import mdraid


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-C', type=str, dest='source_command')
    parser.add_argument('-p', dest='pretty', action='store_true',
                        help='Human-readble, pretty format')
    return parser.parse_args()


def zabbix_lld(entries):
    data = []

    for e in entries:
        lld_entries = {
            '{#DEVICE}': e['dev'],
            '{#NUM_MEMBER_DEVICES}': e['total'],
        }

        data.append(lld_entries)

    return {'data': data}


def main():
    args = get_args()

    lines = mdraid.read_proc_mdstat(cmd=args.source_command)
    entries = mdraid.parse_lines(lines)

    data = zabbix_lld(entries)

    if args.pretty:
        pprint.pprint(data)
    else:
        print(json.dumps(data))


if __name__ == '__main__':
    main()
