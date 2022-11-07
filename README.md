# Dockermonitor

collect command `docker stats` metric data to graphite and display by grafana.

## Getting started

modify config file config.toml,  put it into directory /opt/dockermonitor and run deploy command below.

## Test and Deploy

```bash
#!/bin/bash
#
# William Guozi
# https://www.cnblogs.com/William-Guozi, williamguozi.github.io
# You are free to modify and distribute this code,
# so long as you keep my name and URL in it.
# Created by William Guozi
#

# 获取镜像地址
DOCKER_IMAGE="${1:-{{ williamguozi/dockermonitor:latest }}}"
#获取当前目录名，即为appname
current_dir=`echo $(dirname $(readlink -f "$0"))`
app_name=`echo ${current_dir} | awk -F/ '{print $NF}'`

# 判断容器是否存在，并将其删除
docker pull $DOCKER_IMAGE && \
docker ps -a | awk -F' ' '{print $NF}' | grep "dockermonitor" && \
docker rm -f "dockermonitor" || \
echo "Image $image_url pull failed or No container dockermonitor."

docker run -d \
    --name dockermonitor \
    -v /var/run/docker.sock:/var/run/docker.sock:ro \
    -v /opt/dockermonitor/config.toml:/app/config.toml \
    --cpus 1 \
    -m 1G \
    --restart always \
    $DOCKER_IMAGE
```
