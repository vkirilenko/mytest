FROM centos7:ssh

RUN yum install -y wget java-1.8.0-openjdk                                                              && \
    wget https://archive.apache.org/dist/hadoop/common/hadoop-3.1.2/hadoop-3.1.2.tar.gz -P ~/tmp        && \
    tar xvf ~/tmp/hadoop-3.1.2.tar.gz -C /opt/                                                          && \
    yum clean all && rm -rf /var/cache/yum                                                              && \
    mkdir -p /usr/local/hadoop/ /opt/mount{1,2}/namenode-dir /opt/mount{1,2}/datanode-dir  /opt/mount{1,2}/nodemanager-local-dir  /opt/mount{1,2}/nodemanager-log-dir  /opt/hadoop-3.1.2/logs                                               && \
    ln -s /opt/hadoop-3.1.2/ /usr/local/hadoop/current                                                  && \
    groupadd hadoop -g 2100                                                                && \
    useradd -m -s /bin/bash -g hadoop -u 2000 -p "$(openssl passwd -crypt hadoop)" hadoop  && \
    useradd -m -s /bin/bash -G hadoop -u 2001 -p "$(openssl passwd -crypt hdfs)" hdfs      && \
    useradd -m -s /bin/bash -G hadoop -u 2002 -p "$(openssl passwd -crypt yarn)" yarn      && \
    chmod -R g+sw /opt/hadoop-3.1.2/                               && \
    chown 2000:2100 -R /opt/hadoop-3.1.2/                          && \
    chown -R 2001:2100 /opt/mount{1,2}/namenode-dir                && \
    chown -R 2002:2100 /opt/mount{1,2}/nodemanager-local-dir       && \
    chown -R 2002:2100 /opt/mount{1,2}/nodemanager-log-dir         && \
    chown -R 2001:2100 /opt/mount{1,2}/datanode-dir               

ENV  JAVA_HOME=/usr/lib/jvm/jre
ENV  PATH $PATH:$JAVA_HOME/bin
ENV  HADOOP_HOME=/usr/local/hadoop/current/
ENV  PATH $PATH:$HADOOP_HOME/bin

COPY --chown=2000:2100 ./config/* /usr/local/hadoop/current/etc/hadoop/

USER hadoop
RUN mkdir /home/hadoop/.ssh                                     && \
    ssh-keygen -t rsa -f ~/.ssh/id_rsa -P ''                    && \
    cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys            

EXPOSE 22
EXPOSE 8088
EXPOSE 8080
EXPOSE 8042
EXPOSE 9870
EXPOSE 9864

USER root
CMD ["/usr/sbin/sshd","-D"]
