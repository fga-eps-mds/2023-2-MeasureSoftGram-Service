build:
  docker:
    web: Dockerfile
run:
  web: gunicorn src/config.wsgi:application --bind 0.0.0.0:$PORT --timeout 10000 --log-file -