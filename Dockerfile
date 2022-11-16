FROM ubuntu:20.04

RUN apt update
RUN apt install -y \
    python3.8 \
    python3-pip\
    git 

RUN pip3 install pygame

RUN git clone https://github.com/msiden/gold_thief.git
WORKDIR gold_thief
RUN git checkout containerization

CMD ["python3 gold_thief.py"]
