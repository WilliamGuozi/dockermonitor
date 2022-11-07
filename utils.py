# This Python file uses the following encoding: utf-8
import logging
from colorlog import ColoredFormatter
import toml
from docker import APIClient
from graphyte import Sender
import subprocess
import re


class Utils:
    def __init__(self, file_path='./config.toml'):
        self.configure = toml.load(file_path)
        self.config_dict = Utils.flat_x(self.configure, dict)
        self.logger = self.get_logger(self.config_dict['log.level'])
        self.logger.debug(self.config_dict)

    def get_logger(self, log_level='debug'):
        level = self.get_level(log_level)
        if level == logging.DEBUG:
            logFormat = "%(asctime)s %(log_color)s %(levelname)-8s%(reset)s %(log_color)stheadName:%(threadName)s %(log_color)sfuncName:%(funcName)s %(log_color)s%(message)s%(reset)s"
        else:
            logFormat = "%(asctime)s %(log_color)s%(levelname)-8s%(reset)s %(log_color)s%(message)s%(reset)s"
        logging.root.setLevel(level)
        formatter = ColoredFormatter(logFormat)
        stream = logging.StreamHandler()
        stream.setLevel(level)
        stream.setFormatter(formatter)
        logger = logging.getLogger('pythonConfig')
        logger.setLevel(level)
        logger.addHandler(stream)
        logger.info("log level: {}".format(log_level))
        return logger

    @staticmethod
    def get_level(log_level='debug'):
        level = log_level
        if level == 'info':
            level = logging.INFO
        elif level == 'debug':
            level = logging.DEBUG
        elif level == 'error':
            level = logging.ERROR
        elif level == 'warning':
            level = logging.WARNING
        else:
            level = logging.INFO
        return level

    # flat list and dict
    @staticmethod
    def flat_x(x, types=(dict, list)):
        """
        flat x
        :param x: dict
        :param types: (dict,list) or dict
        :return: dict
        """
        x_dict = {}
        for item in Utils.flat(x, types):
            key, value = item
            x_dict[key] = value
        return x_dict

    @staticmethod
    def flat(x, types):
        for key, value in Utils.iter_x(x):
            if isinstance(value, types):
                for k, v in Utils.flat(value, types):
                    k = f'{key}.{k}'
                    yield k, v
            else:
                yield key, value

    @staticmethod
    def iter_x(x):
        if isinstance(x, dict):
            for key, value in x.items():
                yield key, value
        elif isinstance(x, list):
            for index, value in enumerate(x):
                yield index, value

    @staticmethod
    def translate(str):
        mather = re.findall('[\d\.]+|[\w\.]+', str)
        num, unit = float(mather[0]), mather[1].lower()
        if unit in ['tib', 'tb']:
            return num * 1024
        elif unit in ['gib', 'gb']:
            return num
        elif unit in ['mib', 'mb']:
            return num / 1024
        elif unit in ['kib', 'kb']:
            return num / 1024 / 1024
        elif unit in ['b']:
            return num / 1024 / 1024 / 1024


util = Utils(file_path='./config.toml')
config_dict = util.config_dict
logger = util.logger


class DockerMetric:
    '''
    design for monitor Docker metric
    get ids list of running
    get stats by id
    get_metrics function to transfer stats to metric for graphite
    '''

    def __init__(self, base_url='unix://var/run/docker.sock'):
        self.client = APIClient(base_url=base_url)
        self.container_list = []
        self.id_name_dict = {}
        # output = """
        # {container:focused_rhodes,memory:{raw:300KiB / 7.765GiB,percent:0.00%},cpu:0.00%,PIDs:1,BlockIO:0B / 0B,NetIO:1.15kB / 0B}
        # {container:quirky_ganguly,memory:{raw:352MiB / 2GiB,percent:0.02%},cpu:0.00%,PIDs:1,BlockIO:0B / 0B,NetIO:5.73kB / 0B}
        # """
        self.pattern = """{container:(?P<container>[\w\-\.]+),memory:{raw:(?P<memory_use>[\w\.]+) / (?P<memory_limit>[\w\.]+),percent:(?P<memory_per>[\w\.]+)%},cpu:(?P<cpu>[\w\.]+)%,PIDs:(?P<PIDs>[\w\.]+),BlockIO:(?P<BlockIn>[\w\.]+) / (?P<BlockOut>[\w\.]+),NetIO:(?P<NetIn>[\w\.]+) / (?P<NetOut>[\w\.]+)}"""
        self.regex = re.compile(self.pattern)

    def containers(self):
        return self.client.containers()

    def container_ids(self):
        for container in self.containers():
            self.container_list.append(container['Id'])
        self.container_list = list(set(self.container_list))
        return self.container_list

    def get_stats(self, id):
        return Utils.flat_x(self.client.stats(id, decode=False, stream=False), (dict, list))

    def get_name(self, id):
        pass

    # get metric dict by id
    def get_metrics(self, id):
        stats = self.get_stats(id)
        logger.debug(f'get_metrics stats: {stats}')
        metrics_dict = Utils.flat_x(stats)
        logger.debug(f'get_metrics metric_dict: {stats}')
        return metrics_dict

    def docker_stats(self):
        command = """
        docker stats --no-stream --format  "{container:{{ .Name }},memory:{raw:{{ .MemUsage }},percent:{{ .MemPerc }}},cpu:{{ .CPUPerc }},PIDs:{{ .PIDs }},BlockIO:{{ .BlockIO }},NetIO:{{ .NetIO }}}"
        """
        # {container:devops-redis,memory:{raw:8.934MiB / 15.51GiB,percent:0.06%},cpu:0.12%,PIDs:4,BlockIO:9.52MB / 0B,NetIO:0B / 0B}
        recode, output = subprocess.getstatusoutput(command)
        logger.debug(f'recode:{recode} output:{output}')
        # """{container:(?P<container>[\w\-]+),memory:{raw:(?P<memory_use>[\w\.]+) / (?P<memory_limit>[\w\.]+),percent:(?P<memory_per>[\w\.]+)%},cpu:(?P<cpu>[\w\.]+)%,PIDs:(?P<PIDs>[\w\.]+),BlockIO:(?P<BlockIn>[\w\.]+) / (?P<BlockOut>[\w\.]+),NetIO:(?P<NetIn>[\w\.]+) / (?P<NetOut>[\w\.]+)}"""
        for matcher in self.regex.finditer(output):
            logger.debug(f'matcher: {matcher}')
            g = matcher.groupdict()
            metric_dict = {}
            for key, value in g.items():
                logger.debug(f'metric kv: key:{key} value:{value}')
                if key in ['memory_use', 'memory_limit', 'BlockIn', 'BlockOut', 'NetIn', 'NetOut']:
                    # Gb
                    value = Utils.translate(value)
                elif key in ['memory_per', 'cpu']:
                    value = float(value)
                elif key in ['PIDs']:
                    value = int(value)
                logger.debug(f' after deal with, metric kv: key:{key} value:{value}')
                metric_dict[key] = value
            yield metric_dict


class GraphiteClient:
    '''
    graphite client
    keep alive with graphite server
    '''

    def __init__(self, host, port, prefix):
        self.host = host
        self.port = port
        self.prefix = prefix
        self.client = Sender(host, port, prefix=prefix)

    def send(self, metric, value):
        self.client.send(metric, value)
