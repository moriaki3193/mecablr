FROM alpine:3.8

LABEL maintainer="Moriaki Saigusa <moriaki3193@gmail.com>"

WORKDIR /mecablr

COPY ./app/ /mecablr/

RUN apk --no-cache add \
        python3 \
        python3-dev \
        build-base \
        tzdata \
    && cp /usr/share/zoneinfo/Asia/Tokyo /etc/localtime \
    && rm -rf /var/lib/apt/lists/* \
    && pip3 install --upgrade pip \
    && pip3 install -r requirements.txt

CMD [ "gunicorn", "wsgi:app", "--bind", "0.0.0.0:5000" ]
