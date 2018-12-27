FROM python:3
RUN apt-get update && apt-get install -y --no-install-recommends apt-utils 
RUN apt-get install -y supervisor 
RUN mkdir -p /var/log/supervisor
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

COPY helpers.py /
COPY backtest.sqlite /
COPY requirements.txt /
COPY app.py /
COPY static /static
COPY templates /templates
RUN pip3 install -r requirements.txt

EXPOSE 5005
CMD ["/usr/bin/supervisord","-c/etc/supervisor/conf.d/supervisord.conf"]
