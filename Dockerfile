FROM python:3.9.10-alpine as builder
MAINTAINER "WilliamGuo <634206396@qq.com>"

ENV APP_NAME=dockermonitor
RUN apk update && \
    apk add binutils && \
    apk add openssl && \
    apk add gcc && \
    apk add g++

WORKDIR /build/
COPY / /build/
RUN pip install --upgrade pip && \
    pip install -r requirement
RUN python -OO -m PyInstaller --onefile main.py --clean --name ${APP_NAME} \
    --key=`openssl rand -base64 16 | cut -c1-16`



FROM alpine:3.14
MAINTAINER "WilliamGuo <634206396@qq.com>"

RUN apk update && \
    apk add docker

WORKDIR /app/
COPY --from=builder /build/dist/${APP_NAME} /app/
RUN chmod +x /app/${APP_NAME}

ENTRYPOINT ["/app/dockermonitor"]
