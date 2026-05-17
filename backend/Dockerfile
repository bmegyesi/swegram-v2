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

COPY build_dependencies /root/build_dependencies
COPY dist/swegram-${VERSION}-py3-none-any.whl /dist/swegram-${VERSION}-py3-none-any.whl
RUN pip install dist/swegram-${VERSION}-py3-none-any.whl

RUN swegram-build
RUN rm -rf build_dependencies

EXPOSE 8000

ENTRYPOINT [ "bash", "-c", "uvicorn server.run:app --host 0.0.0.0 --port 8000" ]
