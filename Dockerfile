FROM ubuntu:20.04

RUN apt update
RUN apt install -y python3.8
RUN apt install -y python3-pip==2.0.0
RUN apt install -y git

RUN git clone https://github.com/msiden/gold_thief.git
