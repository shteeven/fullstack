apt-get -qqy update
apt-get -qqy install postgresql python-psycopg2
apt-get -qqy install python-flask python-sqlalchemy
apt-get -qqy install python-pip
pip install bleach
pip install oauth2client
pip install flask==0.9
pip install Flask-Login==0.1.3
pip install google-api-python-client
pip install requests
pip install httplib2

su postgres -c 'createuser -dRS vagrant'
su vagrant -c 'createdb'
su vagrant -c 'createdb forum'
su vagrant -c 'psql forum -f /vagrant/forum/forum.sql'
su vagrant -c 'createdb tournament'
su vagrant -c 'psql forum -f /vagrant/tournament/tournament.sql'
su vagrant -c 'createdb restaurant'
su vagrant -c 'psql forum -f /vagrant/restaurant/restaurant.sql'

vagrantTip="[35m[1mThe shared directory is located at /vagrant\nTo access your shared files: cd /vagrant(B[m"
echo -e $vagrantTip > /etc/motd


