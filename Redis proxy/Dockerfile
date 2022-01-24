FROM golang:1.10
RUN mkdir /redis-sentinel-proxy
ADD . /redis-sentinel-proxy/
WORKDIR /redis-sentinel-proxy
RUN apt-get update && \
    apt-get install redis-tools -y && \
    go build -o redis-sentinel-proxy . && \
    mv /redis-sentinel-proxy/redis-sentinel-proxy /usr/local/bin/redis-sentinel-proxy

ENTRYPOINT ["/usr/local/bin/redis-sentinel-proxy"]
CMD ["-master", "mymaster"]
