#!/usr/bin/env python3
import subprocess
import argparse
import configparser
import sys
import os
import stat


def execute_code(lines, indecies_tuple):
    with open("temp.sh", 'w') as out_file:
        out_file.write("#!/bin/bash\n")
        for i in range(indecies_tuple[0], indecies_tuple[1]):
            out_file.write(lines[i])
            out_file.write('\n')
        out_file.write('\n')
    os.chmod("temp.sh", stat.S_IRWXU)
    subprocess.run(["./temp.sh"])
    os.remove("temp.sh")

def main():
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

    # Parse MD file
    p1 = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=FNULL)
    p1_stdout, p1_stderr = p1.communicate()
    stdout_split = p1_stdout.split(b'\n')
    in_snippet = False
    snippet_list = []

    # Extract the index ranges of each snippet
    for counter, line in enumerate(stdout_split):
        if line != b'':
            if line == b'```' and not in_snippet:
                in_snippet = True
                start_of_snippet = counter + 1
            elif line == b'```':
                in_snippet = False
                end_of_snippet = counter
                snippet_list.append((start_of_snippet, end_of_snippet))
            else:
                stdout_split[counter] = stdout_split[counter].decode("utf-8")
                continue

    # List snippets
    if args.snippet == 'ls':
        for counter, snippet in enumerate(snippet_list):
            snippet_lines = stdout_split[snippet[0]: snippet[1]]
            print (str(counter) + ':')
            for line in snippet_lines:
                print (line)
            print ()

    # Execute snippet by serial number
    elif args.snippet.isnumeric():
        if int(args.snippet) < 0 or int(args.snippet) >= len(snippet_list):
            print ("Outside of snippet range")
            sys.exit(1)
        execute_code(stdout_split, snippet_list[int(args.snippet)])

    # Execute snippet by keyword
    else:
        for counter, snippet_indecies in enumerate(snippet_list):
            start, end  = snippet_indecies[0], snippet_indecies[1]
            first_line = stdout_split[start]
            line_split = first_line.split(' ')
            if args.snippet == line_split[3]:
                execute_code(stdout_split, snippet_indecies)
                break


if __name__ == "__main__":
    main()