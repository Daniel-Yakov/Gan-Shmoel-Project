FROM mysql:5.7
RUN apt update
# Setting MySQL Database Environment Variables
ENV ENV MYSQL_USER="root"
ENV MYSQL_ROOT_PASSORD="root"
ENV MYSQL_DATABASE="weight"
COPY weightdb.sql /var/lib/mysql 
ENTRYPOINT mysql -uroot -p$(MYSQL_ROOT_PASSORD)