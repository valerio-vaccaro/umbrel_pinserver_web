FROM python:3.9-slim

WORKDIR /app
ADD . /app
RUN git submodules update ---init
RUN pip install -r requirements.txt
RUN pip install -r blind_pin_server/requirements.txt

EXPOSE 8081
CMD ["python", "app.py"]
