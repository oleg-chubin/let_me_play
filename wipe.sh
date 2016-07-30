#!/bin/bash
root_dir=`pwd`
GEOGRAPHY=0
POSTGIS_SQL=postgis.sql

SYSTEM_DEPS="unzip binutils libgeos-c1 libxml2 libpq-dev build-essential"
PYTHON_DEPS="python-software-properties python2.7-dev python-setuptools python-pip python-virtualenv"
PG_DEPS="postgresql-9.3 postgresql-9.3-postgis-2.2 postgresql-client-9.3 postgresql-contrib-9.3 postgresql-server-dev-9.3"
GDAL="gdal-bin libgeos-dev libgdal1-dev libxml2-dev libxml2-dev libproj-dev"

COMB="$SYSTEM_DEPS $PYTHON_DEPS $PG_DEPS $GDAL"

#for package in $COMB
#do
#dpkg -l $package | grep "$package" >/dev/null
#    if [ "$?" -eq "1" ]; then
#echo "$package is not installed, try to install..."
#       sudo apt-get -y install $package
#    fi
#dpkg -l $package | grep "$package" >/dev/null
#    if [ "$?" -eq "1" ]; then
#echo "Can not install $package from repository. Try install it manually"
#       exit 1
#    else
#echo "Package $package ...ok"
#    fi
#done

POSTGIS_TEMPLATE=$(sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -w template_postgis | wc -l)
PS_SUDO="sudo -u postgres"

if [ "$POSTGIS_TEMPLATE" -eq "0" ];then
echo "Postgis template not found"
      if [ -d "/usr/share/postgresql/9.3/contrib/postgis-2.2/" ];then
POSTGIS_SQL_PATH=/usr/share/postgresql/9.3/contrib/postgis-2.2/
         GEOGRAPHY=1
      fi

$PS_SUDO createdb -E UTF8 template_postgis && \
( $PS_SUDO createlang -d template_postgis -l | grep plpgsql || $PS_SUDO createlang -d template_postgis plpgsql ) && \
$PS_SUDO psql -d postgres -c "UPDATE pg_database SET datistemplate='true' WHERE datname='template_postgis';" && \
$PS_SUDO psql -d template_postgis -f $POSTGIS_SQL_PATH/$POSTGIS_SQL && \
$PS_SUDO psql -d template_postgis -f $POSTGIS_SQL_PATH/spatial_ref_sys.sql && \
$PS_SUDO psql -d template_postgis -c "GRANT ALL ON geometry_columns TO PUBLIC;" && \
$PS_SUDO psql -d template_postgis -c "GRANT ALL ON spatial_ref_sys TO PUBLIC;"

if [ $GEOGRAPHY -eq 1 ];then
$PS_SUDO psql -d template_postgis -c "GRANT ALL ON geography_columns TO PUBLIC;"
fi
fi

$PS_SUDO dropdb let_me_play
$PS_SUDO createdb -T template_postgis let_me_play

$PS_SUDO psql << EOF

CREATE USER let_me_play WITH PASSWORD 'let_me_play';
ALTER USER let_me_play CREATEDB;
GRANT ALL PRIVILEGES ON DATABASE let_me_play TO let_me_play;

\q
EOF

# pg_restore tips
#dropdb -h localhost -p 5432 -U unistorage unistorage
#pg_restore -h localhost -p 5432 -U unistorage -C -d postgres ~/dbdump/unistorage.dump
