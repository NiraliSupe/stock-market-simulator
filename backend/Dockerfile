FROM python:3.7

RUN set -x \
    && apt-get -qq update \
    && apt-get install -yq --no-install-recommends vim \
    tree \
    curl \
    libsasl2-dev \
    && apt-get purge -y --auto-remove \
    && rm -rf /var/lib/apt/lists/*

ADD requirements.pip /requirements.pip

RUN pip install --upgrade pip && pip install -r requirements.pip

ADD backend /backend

WORKDIR /backend
