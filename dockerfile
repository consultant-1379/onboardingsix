FROM armdocker.rnd.ericsson.se/proj_oss_releases/enm/eric-enm-os-builders/ubuntu/python27/1.1.0-1

WORKDIR /opt/ericsson/nr-nsa-systems-topology

COPY ./requirements.txt ./requirements.txt

RUN pip install -r requirements.txt

COPY ./ ./

RUN ["chmod", "+x", "//opt/ericsson/nr-nsa-systems-topology/wait.sh"]

CMD ["/bin/bash"]