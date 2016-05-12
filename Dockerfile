from pandada8/alpine-python:3
run pip install pyyaml --no-cache-dir && apk add --update rsync openssh-client
add mirrord /app/mirrord
workdir /app
cmd python mirrord/daemon.py -c /app/config.yml
