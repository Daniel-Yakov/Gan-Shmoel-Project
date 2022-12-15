FROM python
# Updates the package lists, install vim and ping commands
RUN apt update && apt install vim -y && apt install iputils-ping -y
# Installs Flask module, pymysql and cryptography modules, along with upgrading pip
COPY . .
RUN pip install cryptography
RUN pip install --upgrade pip
RUN pip install -r req.txt
# Copying the required Python scripts into the container's app directory
# COPY /my_sql/weightdb.sql .
# ENTRYPOINT ["python3", "weight.py"]
