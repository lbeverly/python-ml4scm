# create Ubuntu as base image
FROM ubuntu:20.04

# install packages
RUN apt-get update && apt-get install -y git python3.8 python3-pip curl entr
COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

RUN curl -L -O https://water.usgs.gov/water-resources/software/PHREEQC/phreeqc-3.7.3-15968.tar.gz \
  && tar xvzf phreeqc-3.7.3-15968.tar.gz \
  && cd phreeqc-3.7.3-15968 \
  && ./configure --prefix=/usr \
  && make \
  && make install

EXPOSE 8888

CMD ["jupyter-notebook", "--port=8888", "--no-browser", "--ip=0.0.0.0", "--allow-root"]

