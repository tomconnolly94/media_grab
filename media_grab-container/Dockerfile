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

# make directories that the program requires
RUN mkdir $PROJDIR/logs
RUN mkdir $PROJDIR/data

# COPY .env ${PROJDIR}/.env
COPY ./templates/env-example $PROJDIR/.env
COPY ./templates/MediaIndex-template.json $PROJDIR/data/MediaIndex.json

# install cron job and config access rights
COPY ./scripts/media_grab.cronjob /etc/cron.d/media_grab
RUN chmod 0644 /etc/cron.d/media_grab

# run cron and tail, a cmd that never returns, to keep the container running
CMD cron -f
