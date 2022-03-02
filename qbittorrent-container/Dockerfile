FROM lscr.io/linuxserver/qbittorrent

ARG PROJDIR=/proj-dir

WORKDIR $PROJDIR

ADD . $PROJDIR

RUN apt-get update

CMD ./entrypoint.sh