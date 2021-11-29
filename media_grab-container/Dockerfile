# Use the node base image
FROM node:slim

ARG PROJDIR=/proj-dir
ARG WEBAPPDIR=$PROJDIR/webapp

# Set the working directory to $PROJDIR
WORKDIR $PROJDIR
# Copy the current directory contents into the container
ADD . $PROJDIR

# install apt dependencies
RUN apt-get update
RUN apt-get -y install cron
RUN apt-get install -y python3
RUN apt-get install -y python3-pip

# Install pip dependencies
RUN pip3 install -r requirements.txt

# Install npm dependencies
RUN npm install --prefix $WEBAPPDIR/client

# run frontend static file build
RUN $WEBAPPDIR/client/node_modules/gulp/bin/gulp.js --gulpfile $WEBAPPDIR/client/build/gulpfile.js build

# make directories that the program requires
RUN mkdir /var/log/media_grab
RUN mkdir $PROJDIR/data
RUN chmod 0600 /var/log/media_grab

COPY ./templates/MediaIndex-template.json /data-volume/MediaIndex.json

# install cron job and config access rights
COPY ./scripts/media_grab.cronjob /etc/cron.d/media_grab
RUN chmod 0644 /etc/cron.d/media_grab

# run entrypoint script
CMD ./entrypoint.sh $WEBAPPDIR
