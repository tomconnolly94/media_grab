FROM lscr.io/linuxserver/qbittorrent

ARG PROJDIR=/proj-dir

WORKDIR $PROJDIR

ADD . $PROJDIR

RUN apk update

CMD ./entrypoint.sh
