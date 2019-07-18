# MagicHardening

With magichardening you can securize some services and apps on debian,ubuntu and centos. The list of services that checks is:

- Apache
- Nginx
- SSH
- PHP
- MySQL
- NTP
 
And checks backup files on DocumentRoot of VirtualServers on webservers to prevent that an attacker stole it with enumeration attacks.

Software installed in debian systems: 

- unhide

Note: When you execute the python script he do a backup into /tmp directory in hidden mode. When they finish, please check /tmp and delete old files. 
