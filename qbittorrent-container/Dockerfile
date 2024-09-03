# FROM linuxserver/qbittorrent
FROM linuxserver/qbittorrent:arm32v7-4.5.3

ARG PROJDIR=/proj-dir

WORKDIR $PROJDIR

ADD . $PROJDIR

RUN apk update

# must use ENTRYPOINT in order to pass ENV vars through to script
ENTRYPOINT ["./entrypoint.sh"]
