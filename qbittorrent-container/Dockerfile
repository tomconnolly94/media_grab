FROM lscr.io/linuxserver/qbittorrent

ARG PROJDIR=/proj-dir

WORKDIR $PROJDIR

ADD . $PROJDIR

RUN apk update

# must use ENTRYPOINT in order to pass ENV vars through to script
ENTRYPOINT ["./entrypoint.sh"]
