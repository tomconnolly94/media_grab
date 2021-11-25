FROM ubuntu:latest

ARG PROJDIR=/proj-dir

# Set the working directory to /src
WORKDIR $PROJDIR
# Copy the current directory contents into the container
ADD . $PROJDIR

# install apt dependencies
RUN apt-get update && apt-get -y install cron
RUN apt-get install -y python3
RUN apt-get install -y python3-pip

# Install pip dependencies
RUN pip3 install -r requirements.txt

# install env file
RUN echo "##### ATTENTION: Please make sure you have inserted your values into env-template! #####"

RUN mkdir $PROJDIR/logs
RUN mkdir $PROJDIR/data

RUN ls $PROJDIR/templates

# COPY .env ${PROJDIR}/.env
COPY ./templates/env-example $PROJDIR/.env
COPY ./templates/MediaIndex-template.json $PROJDIR/data/MediaIndex.json

# install cron job
COPY ./scripts/media_grab.cronjob /etc/cron.d/media_grab

# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/media_grab
# Apply cron job
# RUN crontab /etc/cron.d/media_grab

# Run the command on container startup
#CMD cron 
#&& tail -f $PROJDIR/logs/*

# cmd that never returns, to keep the container running
ENTRYPOINT ["tail", "-f", "/dev/null"]