FROM python:3.8.16-slim-bullseye
# Updates the package lists, install vim and ping commands
RUN apt update && apt install vim -y && apt install iputils-ping -y
# Installs Flask module, pymysql and cryptography modules, along with upgrading pip
COPY req.txt .
RUN pip install --upgrade pip
RUN pip install -r req.txt
# Copying the required Python scripts into the container's app directory
WORKDIR /app
COPY weight.py .
COPY conncetion.py .
ENTRYPOINT ["python3", "weight.py"]