FROM docker
RUN apk add --no-cache git
RUN apk add --update --no-cache python3
RUN apk add --update py-pip
COPY requirements.txt /ci
RUN pip install -r 
COPY . /ci
ENTRYPOINT [ "python3", "ci.py" ]
