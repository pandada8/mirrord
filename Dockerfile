from pandada8/alpine-python:3
run pip install pyyaml --no-cache-dir && apk add --update rsync && rm -rf /var/cache/*
add mirrord /app/mirrord
workdir /app
cmd python mirror/daemon.py -f /app/config.yaml
