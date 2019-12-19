#!/usr/bin/env python3

import subprocess
import argparse
import configparser
import sys
import os
import stat

config = configparser.ConfigParser()
config.sections()
config.read("inventory.ini")

parser = argparse.ArgumentParser()
parser.add_argument("group", help="group help")
parser.add_argument("snippet", help="snippet help")
args = parser.parse_args()

try:
    if "local" == args.group:
        command = ["cat", "README.md"]
    elif args.group.startswith('/'):
        command = ["cat", args.group]
    elif "http" in args.group:
        url = args.group
        command = ["curl", "-s", url]
    else:
        url = config["Mapping"][args.group]
        command = ["curl", "-s", url]
except KeyError:
    print("Cant find group in inventory.ini")
    sys.exit()

FNULL = open(os.devnull, 'w')

# Fetch the MD, convert to XML
p1 = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=FNULL)
p2 = subprocess.Popen(["pandoc", "-f", "markdown", "-t", "html"], stdin=p1.stdout, stdout=subprocess.PIPE, stderr=FNULL)
p3 = subprocess.Popen(["xmlstarlet", "fo", "--html", "--dropdtd"], stdin=p2.stdout, stdout=subprocess.PIPE, stderr=FNULL)
stdout, stderr = p3.communicate()

p4 = subprocess.Popen(
    ["xmlstarlet", "sel", "-t", "-v", "count(//code)"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
)
stdout2, stderr = p4.communicate(stdout)

code_count = int(stdout2)
for x in range(1, code_count + 1):
    p4 = subprocess.Popen(
        ["xmlstarlet", "sel", "-t", "-v", "(//code)[" + str(x) + "]"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )
    stdout2, stderr = p4.communicate(stdout)

    if args.snippet == 'ls':
        print(str(x) + ':')
        stdout2 = stdout2.decode("utf-8")
        print(stdout2 + '\n')
    elif args.snippet.isnumeric():
        if str(x) == args.snippet:
            stdout2 = stdout2.decode("utf-8")
            with open("temp.sh", 'w') as out_file:
                out_file.write("#!/bin/bash\n")
                out_file.write(stdout2)
                out_file.write('\n')
            os.chmod("temp.sh", stat.S_IRWXU)
            subprocess.run(["cat", "./temp.sh"])
            print("-------")
            subprocess.run(["./temp.sh"])
    else:
        x = stdout2.split(b'\n')
        pos = x[0].find(b'snip')
        line = x[0][pos:].split()
        if len(line) == 3:
            line[2] = line[2].decode("utf-8")
            if str(line[2]) == args.snippet:
                stdout2 = stdout2.decode("utf-8")
                with open("temp.sh", 'w') as out_file:
                    out_file.write("#!/bin/bash\n")
                    out_file.write(stdout2)
                    out_file.write('\n')
                os.chmod("temp.sh", stat.S_IRWXU)
                subprocess.run(["./temp.sh"])
