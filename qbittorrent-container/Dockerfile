FROM lscr.io/linuxserver/qbittorrent

ARG PROJDIR=/proj-dir

ARG DUMP_COMPLETE_DIR
ENV DUMP_COMPLETE_DIR=$DUMP_COMPLETE_DIR

WORKDIR $PROJDIR

ADD . $PROJDIR

RUN apk update

CMD ./entrypoint.sh
