FROM postgres:11.1

RUN apt-get update \
    && apt-get install -y g++ \
    && apt-get install -y make \
    && apt-get install -y postgresql-server-dev-11 \ 
    && apt-get install -y vim

COPY 0_create_db.sql /docker-entrypoint-initdb.d/0_create_db.sql

WORKDIR /var/lib/postgresql
