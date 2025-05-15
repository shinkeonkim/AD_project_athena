FROM postgres:15

RUN apt-get update && apt-get install -y postgresql-contrib

COPY ./environments/dev/init-pg-extensions.sh /docker-entrypoint-initdb.d/init-pg-extensions.sh
RUN chmod +x /docker-entrypoint-initdb.d/init-pg-extensions.sh
