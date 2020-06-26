FROM alpine:3.12.0 AS builder

ENV LANG C.UTF-8

RUN apk add --no-cache python3 py3-pip && \
    apk add --no-cache --virtual .build-deps build-base python3-dev git && \
    ln -sf /usr/bin/pip3 /usr/bin/pip && \
    ln -sf /usr/bin/python3 /usr/bin/python && \
    pip install --upgrade pip setuptools && \
    pip install --upgrade pip git+https://github.com/pypa/pipenv  # this is due to https://github.com/pypa/pipenv/issues/4337

# This is where pip will install to
ENV PYROOT /pyroot
# A convenience to have console_scripts in PATH
ENV PATH $PYROOT/bin:$PATH
ENV PYTHONUSERBASE $PYROOT

WORKDIR /build
# Install dependencies
ADD Pipfile* ./userservice ./
RUN PIP_USER=1 PIP_IGNORE_INSTALLED=1 pipenv install --system --deploy


####################
# Production image #
####################
FROM alpine:3.12.0 AS prod

ENV LANG C.UTF-8

RUN apk add --no-cache python3 py3-pip && \
    ln -sf /usr/bin/pip3 /usr/bin/pip && \
    ln -sf /usr/bin/python3 /usr/bin/python

ENV PYROOT /pyroot
ENV PATH $PYROOT/bin:$PATH
ENV PYTHONPATH $PYROOT/lib/python:$PATH
# This is crucial for pkg_resources to work
ENV PYTHONUSERBASE $PYROOT

# Finally, copy artifacts
COPY --from=builder $PYROOT/lib/ $PYROOT/lib/

ADD userservice /app

EXPOSE 8080
STOPSIGNAL SIGTERM
ENTRYPOINT ["python", "app"]
