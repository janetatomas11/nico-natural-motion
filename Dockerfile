FROM ubuntu:20.04

WORKDIR thesis

RUN apt update && apt install sudo

ADD install.sh .
