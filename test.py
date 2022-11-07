import subprocess
import re


# def docker_stats():
#     command = """
#     docker stats --no-stream --format  "{container:{{ .Name }},memory:{raw:{{ .MemUsage }},percent:{{ .MemPerc }}},cpu:{{ .CPUPerc }},PIDs:{{ .PIDs }},BlockIO:{{ .BlockIO }},NetIO:{{ .NetIO }}}"
#     """
#     RECODE, OUTPUT = subprocess.getstatusoutput(command)
#     print(f'RECODE: {RECODE}, OUTPUT: {OUTPUT})')
#     return OUTPUT

#
# output = docker_stats()
# print(output)
#
#
# def re_findall(str):
#     m = re.findall('[\d\.]+|[\w\.]+', str)
#     return m[0], m[1]
#
#
# def transfer(str):
#     num, unit = re_findall(str)
#     num, unit = float(num), unit.lower()
#     if unit in ['tib', 'tb']:
#         return num * 1000
#     elif unit in ['gib', 'gb']:
#         return num
#     elif unit in ['mib', 'mb']:
#         return num / 1000
#     elif unit in ['kib', 'kb']:
#         return num / 1000 / 1000
#     elif unit in ['b']:
#         return num / 1000 / 1000 / 1000

    # print(output)


# output = """
# {container:focused_rhodes,memory:{raw:300KiB / 7.765GiB,percent:0.00%},cpu:0.00%,PIDs:1,BlockIO:0B / 0B,NetIO:1.15kB / 0B}
# {container:quirky_ganguly,memory:{raw:352MiB / 2GiB,percent:0.02%},cpu:0.00%,PIDs:1,BlockIO:0B / 0B,NetIO:5.73kB / 0B}
# """
# CONTAINER ID   NAME                      CPU %     MEM USAGE / LIMIT     MEM %     NET I/O         BLOCK I/O        PIDS
output = '''
bdac7db8871d   frontend-consumer   0.04%     18.77MiB / 3.831GiB   0.48%     0B / 0B         2.56MB / 0B      16
0b8a8f020b6a   devops-ktsdb     1.13%     16.89MiB / 2GiB       0.82%     0B / 0B         14.1MB / 0B      37

'''
# pattern = """{container:(?P<container>[\w]+),memory:{raw:(?P<memory_use>[\w\.]+) / (?P<memory_limit>[\w\.]+),percent:(?P<memory_per>[\w\.]+)%},cpu:(?P<cpu>[\w\.]+)%,PIDs:(?P<PIDs>[\w\.]+),BlockIO:(?P<BlockIn>[\w\.]+) / (?P<BlockOut>[\w\.]+),NetIO:(?P<NetIn>[\w\.]+) / (?P<NetOut>[\w\.]+)}"""
pattern = """(?P<container_id>\w+)\s+(?P<name>[\w\-]+)\s+(?P<cpu>[\w\.]+)%\s+(?P<mem_use>[\w\.]+) / (?P<mem_limit>[\w\.]+)\s+(?P<mem_per>[\w\.]+)%\s+(?P<NetIn>[\w\.]+) / (?P<NetOut>[\w\.]+)\s+(?P<BlockIn>[\w\.]+) / (?P<BlockOut>[\w\.]+)\s+(?P<PIDs>[\w\.]+)"""
regex = re.compile(pattern)
for i in regex.finditer(output):
    g = i.groupdict()
    for k, v in g.items():
        # if k in ['memory_use', 'memory_limit', 'BlockIn', 'BlockOut', 'NetIn', 'NetOut']:
        #     v = transfer(v)
        # elif k in ['memory_per', 'cpu']:
        #     # print(v)
        #     v = float(v) * 100
        print(k, v)
    print('----------')

