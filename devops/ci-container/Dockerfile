FROM docker
RUN apk add --no-cache git
RUN apk add --update --no-cache python3
RUN apk add --update py-pip
RUN pip install flask
COPY . .
ENTRYPOINT [ "python3", "ci.py" ]
