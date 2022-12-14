FROM docker
RUN apk add --no-cache git
RUN apk add curl
RUN apk add --update --no-cache python3
RUN apk add --update py-pip
WORKDIR /ci
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
ENTRYPOINT [ "python3", "ci.py" ]
