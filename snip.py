#!/usr/bin/env python3

import subprocess
import argparse
from io import StringIO

parser = argparse.ArgumentParser()
parser.add_argument('group', help='group help')
parser.add_argument('snippet', help='snippet help')
args = parser.parse_args()


# TODO need to install pandoc and xmlstarlet

p1 = subprocess.Popen(['curl', '-s', 'https://gitlab.cee.redhat.com/redsamurai/snip/raw/master/README.md'], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT)

p2 = subprocess.Popen(['pandoc','-f','markdown','-t','html'],stdin=p1.stdout, stdout=subprocess.PIPE)
p3 = subprocess.Popen(['xmlstarlet','fo','--html','--dropdtd'],stdin=p2.stdout, stdout=subprocess.PIPE)
p4 = subprocess.Popen(['xmlstarlet','sel','-t','-v','count(//code)'],stdin=p3.stdout, stdout=subprocess.PIPE)
stdout,stderr = p4.communicate()

code_count = int(stdout)


# Refetch the html
p1 = subprocess.Popen(['curl', '-s', 'https://gitlab.cee.redhat.com/redsamurai/snip/raw/master/README.md'], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT)

p2 = subprocess.Popen(['pandoc','-f','markdown','-t','html'],stdin=p1.stdout, stdout=subprocess.PIPE)
p3 = subprocess.Popen(['xmlstarlet','fo','--html','--dropdtd'],stdin=p2.stdout, stdout=subprocess.PIPE)
stdout,stderr = p3.communicate()

#stdout = stdout.decode("utf-8")

#print(stdout)

###

#file_like_io = StringIO(stdout)

# this one works, using a byte stream
p4 = subprocess.Popen(['xmlstarlet','sel','-t','-v','count(//code)'],stdin=subprocess.PIPE, stdout=subprocess.PIPE)
stdout2,stderr = p4.communicate(stdout)
print(stdout2)





