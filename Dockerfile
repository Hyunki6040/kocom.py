# Use latest Python Alpine image for smaller size and better security
FROM python:3.12-alpine

ENV LANG C.UTF-8
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apk add --no-cache \
    gcc \
    musl-dev \
    linux-headers

# Copy requirements file first for better caching
COPY requirements.txt /
RUN pip3 install --no-cache-dir -r /requirements.txt

# Copy data for add-on
COPY run.sh kocom.conf kocom.py /

WORKDIR /share

RUN chmod a+x /run.sh

CMD [ "/run.sh" ]
