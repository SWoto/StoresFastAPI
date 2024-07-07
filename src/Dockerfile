FROM python:3.11.3

# upgrade pip
RUN pip install --upgrade pip

# get curl for healthchecks
RUN apt install curl

# permissions and nonroot user for tightened security
RUN adduser nonroot --disabled-password
RUN mkdir /home/src/ && chown -R nonroot:nonroot /home/src
RUN mkdir /home/logs/ && chown -R nonroot:nonroot /home/logs
#RUN mkdir -p /var/log/flask-app && touch /var/log/flask-app/flask-app.err.log && touch /var/log/flask-app/flask-app.out.log
#RUN chown -R nonroot:nonroot /var/log/flask-app
WORKDIR /home/src
USER nonroot

# copy all the files to the container
COPY --chown=nonroot:nonroot . .
#COPY --chown=nonroot:nonroot app_users.py app.py
#COPY --chown=nonroot:nonroot /log ./log

# venv
ENV VIRTUAL_ENV=/home/src/venv


# python setup
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
#RUN export FLASK_APP=app.py
RUN pip install -r requirements.txt

WORKDIR /home

# define the port number the container should expose
#EXPOSE 5000

#CMD ["python", "app.py"]