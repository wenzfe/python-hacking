#!/bin/bash
cd /usr/local
wget https://downloads.mysql.com/archives/get/p/23/file/mysql-5.5.62-linux-glibc2.12-x86_64.tar.gz
groupadd mysql
useradd -g mysql mysql
tar -xvf mysql*.tar.gz
rm mysql-*.gz
mv mysql-* mysql
chown root:root mysql
cd mysql
chown -R mysql:mysql *
apt update
apt autoremove
apt install libaio1
apt install libncursesw5
apt install libncurses5
scripts/mysql_install_db --user=mysql
chown -R root .
chown -R mysql data
cp support-files/my-medium.cnf /etc/my.cnf
update-rc.d -f mysql.server defaults
ln -s /usr/local/mysql/bin/mysql /usr/local/bin/mysql

# Quelle: https://ameridroid.com/blogs/ameriblogs/how-to-install-older-version-of-mysql-on-debian-based-systems