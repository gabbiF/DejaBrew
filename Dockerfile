FROM python:3.8

RUN mkdir /usr/app/

COPY . .

RUN pip install -r requirements.txt
RUN pip install Flask-SQLAlchemy --upgrade
RUN pip install SQLAlchemy --upgrade

CMD python app.py
