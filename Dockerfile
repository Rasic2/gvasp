FROM python:3.9

RUN mkdir /app

COPY . /app

WORKDIR /app

RUN /bin/sh -c set -eux; apt-get update; apt-get install tree

RUN echo -e "\033[1;31m Files List Before: \033[0m" && tree

RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple &&  \
    pip install -r requirements.txt --no-cache-dir &&  \
    pip install --no-cache-dir -e .

RUN echo -e "\033[1;31m Files List After: \033[0m" && tree

RUN gvasp -v
