FROM mysql:5.6
COPY ./billingdb.sql /docker-entrypoint-initdb.d/
ENTRYPOINT service mysql start && mysql -u root < ./docker-entrypoint-initdb.d/billingdb.sql
CMD /bin/bash

