FROM python:3.9-slim

WORKDIR /app
ADD . /app
RUN apt update -y
RUN apt install git -y
RUN git submodule update --init
RUN pip install -r requirements.txt
RUN pip install -r blind_pin_server/requirements.txt

EXPOSE 8095
CMD ["python", "app.py"]
