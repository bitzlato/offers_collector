FROM python:3.8-alpine

ENV APP_HOME=/home/app

# Create group "app" and user "app".
RUN addgroup --gid 1000 --system app \
    && adduser --system --home ${APP_HOME} --shell /sbin/nologin --ingroup app --uid 1000 app

WORKDIR $APP_HOME
COPY requirements.txt $APP_HOME/
RUN pip install -r requirements.txt

USER app

COPY --chown=app:app . $APP_HOME
