FROM python:3.10

USER 0:0

ENV PYTHONPATH="$PYTHONPATH:/root/server:/tools/efselab"
ENV SWEGRAM_WORKSPACE=/root

# Python packages
RUN ln -s /usr/bin/python3.10 /usr/bin/python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1 

COPY tools/ /tools
COPY server/ /root/server
COPY run_server.py /root

COPY requirements.server.txt /requirements.txt

RUN pip install -r /requirements.txt --index-url https://pypi.org/simple

WORKDIR /root

ENTRYPOINT [ "uvicorn", "run_server:app", "--reload" ]
