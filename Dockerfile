FROM python:3.8-alpine
COPY . /app
WORKDIR /app
VOLUME /app/output
RUN pip install -r requirements.txt && \
    apk update && apk upgrade && \
    apk add --no-cache bash git openssh
CMD python ./main.py