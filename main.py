# This Python file uses the following encoding: utf-8
from utils import Utils, util, logger, config_dict, GraphiteClient, DockerMetric
import threading
import time
import datetime


def worker(id, interval):
    '''
    deal with from docker server metric， send to graphite
    :param id: container id
    :param gc: GraphiteClient object
    :param interval: how often do it collect
    :return: None
    '''
    metrics = {}
    data_dict = {}
    data_dict['NetRx_pre'] = data_dict['NetTx_pre'] = data_dict['BlockRead_pre'] = data_dict['BlockWrite_pre'] = (-1, -1)
    while True:
        for i in range(2):
            try:
                metrics = dm.get_stats(id)
            except Exception as e:
                logger.error(f'container {id} exit. {e}')
                break
            container_name = metrics['name'].lstrip('/').replace('.', '_')
            dm.id_name_dict[id] = container_name
            count = 0
            timestamp_now = datetime.datetime.strptime(metrics.get('read')[:-4], "%Y-%m-%dT%H:%M:%S.%f").timestamp()
            data_dict['BlockRead_now'] = (timestamp_now, metrics.get('blkio_stats.io_service_bytes_recursive.0.value', -1))
            data_dict['BlockWrite_now'] = (timestamp_now, metrics.get('blkio_stats.io_service_bytes_recursive.1.value', -1))
            data_dict['NetRx_now'] = (timestamp_now, metrics.get('networks.eth0.rx_bytes', -1))
            data_dict['NetTx_now'] = (timestamp_now, metrics.get('networks.eth0.tx_bytes', -1))
            for key in ['BlockRead', 'BlockWrite', 'NetRx', 'NetTx']:
                ts, value = data_dict[f'{key}_pre']
                if ts != -1 and value != -1:
                    # Mbps
                    data_dict[key] = abs((data_dict[f'{key}_now'][1] - data_dict[f'{key}_pre'][1])) / abs((data_dict[f'{key}_now'][0] - data_dict[f'{key}_pre'][0])) * 8 / 1024 / 1024
                    value = data_dict[key]
                    metric = f'{hostname}.{container_name}.{key}'
                    gc.send(metric, value)
                    count += 1
                    logger.debug(f"send to graphite metric: {metric}, value: {value}")
                data_dict[f'{key}_pre'] = data_dict[f'{key}_now']
            logger.info(f'send container {container_name} {count} metrics to {gc.host}:{gc.port}')
            time.sleep(1)
        time.sleep(10)


def worker2(interval):
    '''
    deal with from docker server metric， send to graphite
    :param id: container id
    :param gc: GraphiteClient object
    :param interval: how often do it collect
    :return: None
    '''
    '''
    container quirky_ganguly
    memory_use 0.000352
    memory_limit 2.0
    memory_per 2.0
    cpu 0.0
    PIDs 1
    BlockIn 0.0
    BlockOut 0.0
    NetIn 5.8700000000000005e-06
    NetOut 0.0
    '''
    while True:
        for metrics in dm.docker_stats():
            logger.debug(f'metrics: {metrics}')
            container_name = metrics['container'].replace('.', '_')
            count = 0
            for m, v in metrics.items():
                if isinstance(v, (int, float)):
                    metric = f'{hostname}.{container_name}.{m}'
                    value = v
                    gc.send(metric, value)
                    count += 1
                    logger.debug(f"send to graphite metric: {metric}, value: {value}")
            logger.info(f'send container {container_name} {count} metrics to {gc.host}:{gc.port}')
        time.sleep(interval)


if __name__ == "__main__":
    interval = config_dict['server.interval']
    gc = GraphiteClient(config_dict['graphite.server'], config_dict['graphite.port'], config_dict['graphite.prefix'])
    dm = DockerMetric(config_dict['docker.base_url'])
    hostname = config_dict['server.hostname']
    while True:
        # run one thread for one container
        thread_list = [thread.name for thread in threading.enumerate()]
        logger.info(f'thread for conatiner list:{[dm.id_name_dict.get(thread, thread) for thread in thread_list]}.')
        if 'worker2' not in thread_list:
            t = threading.Thread(target=worker2, name='worker2', args=(interval,))
            t.start()
        # # get all running container id
        # ids = dm.container_ids()
        # for id in ids:
        #     if id not in thread_list:
        #         t = threading.Thread(target=worker, name=id, args=(id, interval))
        #         t.start()
        #         # waiting for thread refresh GraphiteClient object gc's id_name_dict
        #         time.sleep(3)
        #         logger.info(f'thread {id} are running for container {dm.id_name_dict.get(id, id)}')
        time.sleep(interval)
