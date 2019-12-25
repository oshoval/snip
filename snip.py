#!/usr/bin/env python3
import subprocess
import argparse
import configparser
import sys
import os
import stat


def execute_code(lines, indices_tuple, interpreters, type_arg, type_dry, modify):
    with open("temp.sh", 'w') as out_file:
        out_file.write(interpreters[type_arg])
        for i in range(indices_tuple[0], indices_tuple[1]):
            out_file.write(lines[i])
            out_file.write('\n')
        out_file.write('\n')
    os.chmod("temp.sh", stat.S_IRWXU)
    if modify:
        editor = os.getenv('EDITOR', 'vi')
        subprocess.call('%s %s' % (editor, "temp.sh"), shell=True)
    if type_dry:
        with open("temp.sh", 'r') as temp_file:
            content = temp_file.readlines()
            for line in content:
                line = line.rstrip('\n')
                print (line)
    else:
        subprocess.run(["./temp.sh"])
    os.remove("temp.sh")


def main():
    # Initialize config parser for handing the .ini file
    config = configparser.ConfigParser()
    config.sections()
    config.read("inventory.ini")

    # Initialize program's arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("group", help="group help")
    parser.add_argument("snippet", help="snippet help")
    parser.add_argument("-t", "--type", help="interpreter", type=str, default='bash')
    parser.add_argument("-d", "--dry", action='store_true')
    parser.add_argument("-m", "--modify", action='store_true')
    args = parser.parse_args()

    interpreters = {'bash': "#!/bin/bash\n",
                    'python3': "#!/usr/bin/env python3\n",
                    'python2': "#!/usr/bin/env python2\n"}

    if args.type not in interpreters:
        print("Error, interpreter is not recognized")
        sys.exit(1)

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
        sys.exit(1)

    FNULL = open(os.devnull, 'w')

    # Parse MD file
    p1 = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=FNULL)
    p1_stdout, p1_stderr = p1.communicate()
    stdout_split = p1_stdout.split(b'\n')
    in_snippet = False
    snippet_list = []

    # Extract the index ranges of each snippet
    for counter, line in enumerate(stdout_split):
        stdout_split[counter] = line.decode("utf-8")
        line = stdout_split[counter]
        if line != '':
            if line.startswith('```') and not in_snippet:
                in_snippet = True
                start_of_snippet = counter + 1
            elif line.startswith('```'):
                in_snippet = False
                end_of_snippet = counter
                snippet_list.append((start_of_snippet, end_of_snippet))

    # List snippets
    if args.snippet == 'ls':
        for counter, snippet in enumerate(snippet_list):
            snippet_lines = stdout_split[snippet[0]: snippet[1]]
            print (str(counter + 1) + ':')
            for line in snippet_lines:
                print (line)
            print ()

    # Execute snippet
    else:
        if args.snippet.isnumeric():
            if int(args.snippet) < 1 or int(args.snippet) > len(snippet_list):
                print ("Outside of snippets range")
                sys.exit(1)
            snippet_to_run = snippet_list[int(args.snippet) - 1]
        else:
            for counter, snippet_indices in enumerate(snippet_list):
                start, end = snippet_indices[0], snippet_indices[1]
                first_line = stdout_split[start]
                line_split = first_line.split(' ')
                if args.snippet == line_split[3]:
                    execute_code(stdout_split, snippet_indices, interpreters, args.type, args.dry)
                    snippet_to_run = snippet_indices
                    break

        execute_code(stdout_split, snippet_to_run, interpreters, args.type, args.dry, args.modify)


if __name__ == "__main__":
    main()