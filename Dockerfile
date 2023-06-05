FROM joyzoursky/python-chromedriver:3.8
RUN apt-get update && apt-get upgrade -y && apt-get autoremove && apt-get autoclean

RUN mkdir /project
COPY . /project/
WORKDIR /project

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ENTRYPOINT [ "python3", "main.py" ]