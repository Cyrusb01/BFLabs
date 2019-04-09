FROM python:3
RUN apt-get update && apt-get install -y --no-install-recommends apt-utils 
RUN apt-get install -y supervisor 
RUN mkdir -p /var/log/supervisor
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

ADD config.py /
ADD requirements.txt /
ADD gunicorn.conf.py /
ADD app.py /
ADD helpers.py /
ADD variables.py /
ADD static /static
ADD templates /templates
RUN pip3 install -r requirements.txt

CMD ["/usr/bin/supervisord","-c/etc/supervisor/conf.d/supervisord.conf"]
