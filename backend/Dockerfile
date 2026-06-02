FROM python:3.8

ARG VERSION
USER 0:0

ENV PYTHONPATH="/root:/root/tools/efselab"
ENV PATH="$PATH:/root:/root/tools:/root/tools/efselab"
ENV SWEGRAM_WORKSPACE=/root
ENV PRODUCTION=1

# INSTALL openjdk (required for maltparser used in efselab)
RUN apt update && apt install openjdk-17-jdk -y

# Python packages
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY backend/build_dependencies /root/build_dependencies
COPY backend/pyproject.toml /root/pyproject.toml
COPY backend/README.md /root/README.md
COPY backend/requirements.txt /root/requirements.txt
COPY backend/server /root/server
COPY backend/setup.sh /root/setup.sh
COPY backend/swegram_main /root/swegram_main

WORKDIR /root
RUN pip install wheel build
RUN pip install -r requirements.txt
RUN pip install .

RUN swegram-build
RUN rm -rf build_dependencies

EXPOSE 8000

# FROM python:3.8 as runner

# WORKDIR /root
# # Reuse installed dependencies
# COPY --from=builder . .
ENTRYPOINT [ "bash", "-c", "tail -f /dev/null" ]
# COPY backend/pyproject.toml /root/pyproject.toml
# COPY backend/requirements.txt /root/requirements.txt
# COPY backend/server /root/server
# COPY backend/setup.sh /root/setup.sh
# COPY backend/swegram_main /root/swegram_main
# RUN pip install wheel build
# RUN pip install -r requirements.txt
# RUN pip install .

# ENTRYPOINT [ "bash", "-c", "uvicorn server.run:app --host 0.0.0.0 --port 8000 --reload" ]
