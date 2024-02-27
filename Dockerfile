FROM python:3.8

USER 0:0

ENV PYTHONPATH="/root:/root/server:/root/tools/efselab"
ENV PATH="$PATH:/root:/root/server:/root/tools:/root/tools/efselab"
ENV SWEGRAM_WORKSPACE=/root
ENV PRODUCTION=1

# INSTALL openjdk (required for maltparser used in efselab)
RUN apt update && apt install openjdk-17-jdk -y

# Python packages
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1 

COPY build_dependencies /root/build_dependencies
COPY server/ /root/server
COPY app_run.py /root

COPY requirements.server.txt /requirements.txt

# Entry python script to run app
COPY main.py /root

RUN pip install -r /requirements.txt --index-url https://pypi.org/simple

# Add dependencies
COPY swegram_main /root/swegram_main
COPY setup.py /root
COPY build_dependencies /root/build_dependencies
COPY README.md /root
COPY LICENSE.md /root
COPY requirements.txt /root

WORKDIR /root
RUN pip install wheel
RUN pip install .
RUN swegram-build
RUN rm -rf build_dependencies build requirements.txt swegram.egg-info

EXPOSE 8000

ENTRYPOINT [ "bash", "-c", "cd /root && python main.py" ]
