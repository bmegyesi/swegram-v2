FROM python:3.10

USER 0:0

ENV PYTHONPATH="$PYTHONPATH:/root:/root/server:/root/tools/efselab"
ENV PATH="$PATH:/root:/root/server:/root/tools:/root/tools/efselab"
ENV SWEGRAM_WORKSPACE=/root
ENV PRODUCTION=1

# Python packages
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1 

COPY build_dependencies /root/build_dependencies
COPY server/ /root/server
COPY app_run.py /root

COPY requirements.server.txt /requirements.txt

# Entry python script to run app
COPY main.py /root

WORKDIR /root
RUN python -m venv venv && \
    . venv/bin/activate && \
    pip install -r /requirements.txt --index-url https://pypi.org/simple && \
    deactivate

RUN . venv/bin/activate && swegram-build && deactivate
RUN rm -rf build_dependencies requirements.txt

ENTRYPOINT [ "bash", "-c", "source venv/bin/activate && python main.py" ]
