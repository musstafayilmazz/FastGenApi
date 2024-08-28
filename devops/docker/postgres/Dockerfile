FROM postgres:14

RUN apt-get update && apt-get install -y \
    postgresql-server-dev-14 \
    build-essential \
    git \
    && git clone https://github.com/pgvector/pgvector.git \
    && cd pgvector \
    && make \
    && make install \
    && cd .. \
    && rm -rf pgvector \
    && apt-get remove --purge -y git build-essential \
    && apt-get autoremove -y \
    && apt-get clean

CMD ["postgres"]
