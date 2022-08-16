# create Ubuntu as base image
FROM lbeverly/ml4scm-phreeqc:3.7.3

# install packages
RUN pip3 install plotly
COPY runner.sh /runner.sh

EXPOSE 8888

CMD ["/runner.sh"]

