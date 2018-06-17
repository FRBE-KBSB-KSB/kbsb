FROM python:3

WORKDIR /app

COPY kbsb/backend/requirements.txt ./
RUN pip install -r requirements.txt

COPY kbsb/backend/kbsb ./

CMD [ "python", "./manage.py", "runserver" ]