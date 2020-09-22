Meal Paper Development Guide

For apache configuration

    sudo apt-get install libapache2-mod-wsgi-py3

Development setup

Install required system packages:

    sudo apt-get install python3-pip
    sudo apt-get install python3-dev python3-setuptools
    sudo apt-get install libpq-dev
    sudo apt-get install postgresql postgresql-contrib
    sudo apt-get install libmysqlclient-dev
Create www directory where project sites and environment dir

    mkdir /var/www && mkdir /var/envs && mkdir /var/envs/bin

Install virtualenvwrapper

    sudo pip3 install virtualenvwrapper
    sudo pip3 install --upgrade virtualenv

Add these to your bashrc virutualenvwrapper work

    export WORKON_HOME=/var/envs
    export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3
    export PROJECT_HOME=/var/www
    export VIRTUALENVWRAPPER_HOOK_DIR=/var/envs/bin
    source /usr/local/bin/virtualenvwrapper.sh

Create virtualenv

    cd /var/envs && mkvirtualenv --python=/usr/bin/python3 mealpaper
    pip install mysqlclient


Install requirements for a project.

    cd /var/www/mealpaper/api && pip install -r requirements/local.txt

    sudo chown :www-data /var/www/mealpaper
    sudo cp /var/www/mealpaper/api/conf/mealpaper.com.conf /etc/apache2/sites-available/
    sudo cp /var/www/mealpaper/api/wsgi_default.py /var/www/mealpaper/api/wsgi.py


##Database creation
###For psql

    sudo su - postgres
    psql
    DROP DATABASE IF EXISTS mealpaper;
    CREATE DATABASE mealpaper;
    CREATE USER mealpaper_db_manager WITH password '123456ab';
    GRANT ALL privileges ON DATABASE mealpaper TO mealpaper_db_manager;
    ALTER USER mealpaper_db_manager CREATEDB;





##Set up supervisor (pm2)

    $ sudo apt-get install python-software-properties
    $ curl -sL https://deb.nodesource.com/setup_7.x | sudo -E bash -
    $ sudo apt-get install nodejs
    $ cd /var/www/subdomains/codebnb/mealpaper/public_html
    $ pm2 startup ubuntu14
    $ pm2 start scripts/manage_codebnb_init_default_consumer.sh --name property_api_init_default_consumer
    $ pm2 save


###For mysql

    mysql
    mysql > DROP DATABASE IF EXISTS mealpaper;
    mysql > CREATE DATABASE mealpaper CHARACTER SET utf8;
    mysql > CREATE USER 'mealpaper_db_user'@'localhost' IDENTIFIED BY '123456ab';
    mysql > GRANT ALL PRIVILEGES ON mealpaper.* TO 'mealpaper_db_user'@'localhost';
    pip install mysql-to-json 
    mysql-to-json -H localhost -P 3306 -d mealpaper -u mealpaper_db_user -p -e 'SELECT * FROM mealpaper_db_model' > tables.json


Configure rabbitmq-server to run workers.
Add virtual host, and set permissions.

    $ sudo rabbitmqctl add_vhost mealpaper
    $ sudo rabbitmqctl add_user mealpaper_db_user root
    $ sudo rabbitmqctl set_permissions -p mealpaper mealpaper_db_user ".*" ".*" ".*"

###Set up supervisor (pm2)

    $ cd /var/www/mealpaper
    $ pm2 startup ubuntu14
    $ pm2 start scripts/cois_scrap_tasks.sh --name cois_scrap_tasks
    $ pm2 save

### for intergration ABBY FINEREADER

export ABBYY_APPID=YourApplicationId
export ABBYY_APPID=mealpaper_app

export ABBYY_PWD=YourPassword
export ABBYY_PWD=Y3jqv9q05q3rttpcDlcHVEu/

### for install pyocr
pip install pyocr 
sudo apt-get install tesseract-ocr
sudo apt-get install tesseract-ocr-eng
sudo apt-get install tesseract-ocr-ell

