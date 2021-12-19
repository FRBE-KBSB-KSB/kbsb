FROM python:3.9
WORKDIR /workspace
RUN pip install pipenv
COPY Pipfile* /workspace/
COPY libs /workspace/libs/
RUN pipenv install --system --deploy
ENV PATH=$PATH:/workspace/src
ENV PYTHONPATH /workspace/src
COPY backend/kbsb /workspace/src/kbsb
CMD uvicorn --port 8000 --host 0.0.0.0 kbsb:app
