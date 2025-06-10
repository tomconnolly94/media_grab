# Use the node base image
FROM node:22

ARG PROJDIR=/proj-dir
ARG WEBAPPDIR=$PROJDIR/webapp

# Set the working directory to $PROJDIR
WORKDIR $PROJDIR

# Copy the current directory contents into the container
ADD . $PROJDIR

# hack to jump over PEP668
ENV PIP_BREAK_SYSTEM_PACKAGES 1

# install apt dependencies
RUN apt-get update
RUN apt-get install -y python3
RUN apt-get install -y cron
RUN apt-get install -y python3-pip

# Install npm dependencies
RUN npm update -g npm
RUN npm config delete proxy
RUN npm install --prefix $WEBAPPDIR/client

# run frontend static file build
RUN $WEBAPPDIR/client/node_modules/gulp/bin/gulp.js --gulpfile $WEBAPPDIR/client/build/gulpfile.js build

# install test dependencies
RUN pip install -r ./requirements-dev.txt

# create required test directories
RUN mkdir src/test/dummy_directories
RUN mkdir src/test/dummy_directories/dump_complete
RUN mkdir src/test/dummy_directories/logs
RUN mkdir src/test/dummy_directories/recycle_bin
RUN mkdir src/test/dummy_directories/tv

# unit testing
RUN python3 -m unittest discover -s src/test/unit_test/

# clean up test dirs
RUN rm -rf src/test/dummy_directories
RUN rm -rf src/test/dummy_directories/dump_complete
RUN rm -rf src/test/dummy_directories/logs
RUN rm -rf src/test/dummy_directories/recycle_bin
RUN rm -rf src/test/dummy_directories/tv

# uninstall test dependencies
RUN pip uninstall -y -r ./requirements-dev.txt

# install prod dependencies
RUN pip install -r ./requirements.txt

# make directories that the program requires
RUN mkdir /var/log/media_grab
RUN chmod 0666 /var/log/media_grab

# RUN rm /data-volume/MediaIndex.json
# COPY ./templates/MediaIndex-template.json /data/MediaIndex.json

# install cron job and config access rights
COPY ./scripts/media_grab.cronjob /etc/cron.d/media_grab

RUN chmod 0644 /etc/cron.d/media_grab

# run entrypoint script
CMD ./entrypoint.sh $WEBAPPDIR
