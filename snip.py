#!/usr/bin/env python3

import subprocess
import argparse
import configparser
import sys
import os
import stat

# Initialize config parser for handing the .ini file
config = configparser.ConfigParser()
config.sections()
# do we want to hardcode this?
config.read("inventory.ini")

# Initialize program's arguments
parser = argparse.ArgumentParser()
parser.add_argument("group", help="group help")
parser.add_argument("snippet", help="snippet help")
args = parser.parse_args()

# Determine how to fetch MD
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

# Count the number of <code> ... </code> blocks
p4 = subprocess.Popen(
    ["xmlstarlet", "sel", "-t", "-v", "count(//code)"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
)
stdout2, stderr = p4.communicate(stdout)

# Looping on snippets
code_count = int(stdout2)
for x in range(1, code_count + 1):
    p4 = subprocess.Popen(
        ["xmlstarlet", "sel", "-t", "-v", "(//code)[" + str(x) + "]"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )
    stdout2, stderr = p4.communicate(stdout)
    # Generate & print list of available snippets in the current MD file
    if args.snippet == 'ls':
        print(str(x) + ':')
        stdout2 = stdout2.decode("utf-8")
        print(stdout2 + '\n')

    # Execute snippet by its serial number
    elif args.snippet.isnumeric():
        if str(x) == args.snippet:
            stdout2 = stdout2.decode("utf-8")
            # Injecting snippet to a temporary script file
            with open("temp.sh", 'w') as out_file:
                out_file.write("#!/bin/bash\n")
                out_file.write(stdout2)
                out_file.write('\n')
            os.chmod("temp.sh", stat.S_IRWXU)
            subprocess.run(["cat", "./temp.sh"])
            print("-------")
            subprocess.run(["./temp.sh"])
            # should delete the file after execution

    # Execute snippet by keyword
    else:
        # First issue - this else (and probably the 'if' and 'elif' above) is executing for every snippet - even though we just wanted a specific one
        # Second issue - x is not a meaningful name for a variable
        x = stdout2.split(b'\n')
        pos = x[0].find(b'snip')  # locates the starting index of 'snip'
        line = x[0][pos:].split()  # split the line, starting from 'snip'
        if len(line) == 3: # line length should always be 3???? i.e. snip main hello
            line[2] = line[2].decode("utf-8")
            # Execute the right snippet in accordance to the given keyword
            if str(line[2]) == args.snippet:
                stdout2 = stdout2.decode("utf-8")
                # Repeating code!
                with open("temp.sh", 'w') as out_file:
                    out_file.write("#!/bin/bash\n")
                    out_file.write(stdout2)
                    out_file.write('\n')
                os.chmod("temp.sh", stat.S_IRWXU)
                subprocess.run(["./temp.sh"])


# Suggestions:
#1. Refactoring the code
#2. Arrange in functions
#3. Add some extra functionality - ability to run code from different languages
#4. Add comments