build:
  docker:
    web: Dockerfile
run:
  web: gunicorn 2023-2-MeasureSoftGram-Service/src/config.wsgi:application --bind 0.0.0.0:$PORT --timeout 10000 --log-file -