# Setting MySQL Database base image
FROM mysql:5.6

# COPY weightdb.sql to the container
COPY ./weightdb.sql ./docker-entrypoint-initdb.d/

# exposing the default port
EXPOSE 3306