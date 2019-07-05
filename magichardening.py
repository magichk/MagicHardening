#!/usr/bin/python3

import os
import platform

print (" 	 __  __             _      _   _               _            _             ")
print ("	|  \/  | __ _  __ _(_) ___| | | | __ _ _ __ __| | ___ _ __ (_)_ __   __ _ ")
print ("	| |\/| |/ _` |/ _` | |/ __| |_| |/ _` | '__/ _` |/ _ \ '_ \| | '_ \ / _` |")
print ("	| |  | | (_| | (_| | | (__|  _  | (_| | | | (_| |  __/ | | | | | | | (_| |")
print ("	|_|  |_|\__,_|\__, |_|\___|_| |_|\__,_|_|  \__,_|\___|_| |_|_|_| |_|\__, |")
print ("	              |___/                                                 |___/ ")

print ("								       By @magichk")


#Detect OS distribution: debian, centos..
dist = platform.linux_distribution()

if (dist[0] == "debian"):
	#check apache and nginx.
	apache = os.path.exists('/etc/apache2/')
	nginx = os.path.exists('/etc/nginx/')
	php = os.path.exists('/etc/php5/apache2/php.ini')
	ssh = os.path.exists('/etc/ssh/sshd_config')

	#Check other versions of PHP.
	version = 5
	if (php != True):
		php = os.path.exists('/etc/php/7*/apache2/php.ini')
		version = 7

	if (php != True):
		php = os.path.exists('/etc/php/apache2/php.ini')
		version = ""

	#Exist the folder that contains virtualhosts?
	if (apache == True):
		apache = os.path.exists('/etc/apache2/sites-enabled/')


	if (apache == True):
		print ("\033[1;37;40m [+] Checking Apache...")
		#Backup original config
		os.system("cp -Ra /etc/apache2 /tmp/apache2.back")


		#Change ServerSignature
		cmd = os.popen('grep -R "ServerSignature On" /etc/apache2/ | grep -v "#" ').read()
		if cmd:
			os.system("grep -R 'ServerSignature On' /etc/apache2/ | grep -v '#' | cut -d':' -f 1 | xargs -i  sed -i 's/ServerSignature On/ServerSignature Off/g' {} ")
			print ("\033[1;32;40m [PASS] Changing ServerSignature On to Off")
		else:
			print ("\033[1;34;40m [CORRECT] - ServerSignature is Off")

		#Change ServerTokens
		cmd = os.popen('grep -R "ServerTokens OS" /etc/apache2/ | grep -v "#" | grep -v "Prod"').read()
		if cmd:
		        os.system("grep -R 'ServerTokens' /etc/apache2/ | grep -v '#' | grep -v 'Prod' | cut -d':' -f 1 | xargs -i  sed -i 's/ServerTokens OS/ServerTokens Prod/g' {} ")
	        	print ("\033[1;32;40m [PASS] Changing ServerTokens to Prod for hide Apache version")
		else:
			print ("\033[1;34;40m [CORRECT] - ServerTokens value is Prod")
	
		#Change Options. 
		cmd = os.popen('grep -R "Options None" /etc/apache2/sites-enabled/').read()
		if cmd:
			#Canviar la part del \n
			command = "grep -R 'Options' /etc/apache2/sites-enabled/ | cut -d':' -f2 | xargs -I '{}' sed -i 's/Options None/Options -ExecCGI -Indexes -Includes/g' /etc/apache2/sites-enabled/*"
			os.system(command)
			print ("\033[1;32;40m [PASS] Changing Options...")
		else:
			print ("\033[1;34;40m [CORRECT] - Options directive is correct!")
	

		#Add protection to .htaccess file
		files = os.popen("ls /etc/apache2/sites-enabled/").read()
		files = files[:-1]
	
		cmd = os.popen('grep ".httpdoverride" /etc/apache2/sites-enabled/'+files).read()
		if cmd:
			print ("\033[1;34;40m [CORRECT] - The directive of .htaccess file exists, no applying..")
		else:
			flag = 0
			newfile = ""	
			f = open("/etc/apache2/sites-enabled/"+files, "r")
			for line in f:
			#Check the line that finish the virtualhost.
				start = line.find("</VirtualHost>")
				if (start != -1):
					flag = 1
				start = line.find("</Virtualhost>")
				if (start != -1):
					flag = 1
				start = line.find("</virtualhost>")
				if (start != -1):
					flag = 1
	
				if (flag == 1):
					newline = 'AccessFileName .httpdoverride\n<Files ~ "^\.ht">\nOrder allow,deny\nDeny from all\nSatisfy All\n</Files>\n'
					newfile = newfile + newline
					flag = 0
		
				newfile = newfile + line
			f.close()

			f = open("/etc/apache2/sites-enabled/"+files, "w")
			f.write(newfile)
			f.close()

			print ("\033[1;37;40m [-] RESTARTING apache2 service...")
			os.system("systemctl restart apache2")


	#Hardening nginx service
	if (nginx == True):
		print ("\033[1;37;40m [+] Checking nginx...")

		#Backup original config
		os.system("cp -Ra /etc/nginx /tmp/nginx.back")

		#Check if default.conf exists..
		nginx_conf = os.path.exists('/etc/nginx/conf.d/default.conf')
		if (nginx_conf == True):
			cmd = os.popen('grep "sqlmap" /etc/nginx/conf.d/default.conf').read()
			if cmd:
				print ("\033[1;34;40m [CORRECT] - nginx is securitzed!")
			else:
				flag = 0
				newfile = ""
				f = open("/etc/nginx/conf.d/default.conf", "r")
				for line in f:
					#Check the line if it is the start of server.
					start = line.find("server {")
					if (start != -1):
						flag = 1
					start = line.find("server{")
					if (start != -1):
						flag = 1

					if (flag == 1):
						newline = '\tif ($http_user_agent ~* (acunetix|sqlmap|nikto|metasploit|hping3|maltego|nessus|webscarab|sqlsus|sqlninja|aranchni|netsparker|nmap|dirbuster|zenmap|hydra|owasp-zap|w3af|vega|burpsuite|aircrack-ng|whatweb|medusa) ) { \n return 403;\n }\n'
						newline = newline + '\tif ($http_user_agent ~ (msnbot|Purebot|Baiduspider|Lipperhey|Mail.Ru|scrapbot) ) {\nreturn 403;\n}'
						newline = newline + '\tif ($http_user_agent ~* LWP::Simple|wget|libwww-perl) {\nreturn 403;\n}\n'


						newfile = newfile + line + newline
						flag = 2
					if (flag != 2):
						newfile = newfile + line
					else:
						flag = 0
				f.close()
			
				f = open("/etc/nginx/conf.d/default.conf", "w")
				f.write(newfile)
				f.close()
				os.system("systemctl restart nginx")
				print ("\033[1;32;40m [PASS] Config of nginx was securitzed!")

	if (php == True):
		print ("\033[1;37;40m [+] Checking php configuration...")
	
		#Hide php version
		cmd = os.popen('grep -R "expose_php = On" /etc/php'+str(version)+'/apache2/php.ini').read()
		if cmd:
			os.system("sed -i 's/expose_php = On/expose_php = Off/g' /etc/php"+str(version)+"/apache2/php.ini")
			print ("\033[1;32;40m [PASS] Config of php.ini updated")
		else:
			print ("\033[1;34;40m [CORRECT] - php.ini is up to date")

		#Hide errors.

		cmd = os.popen('grep -R "display_errors = On" /etc/php'+str(version)+'/apache2/php.ini').read()
		if cmd:
        	        os.system("sed -i 's/display_errors = Off/display_errors = On/g' /etc/php"+str(version)+"/apache2/php.ini")
                	print ("\033[1;32;40m [PASS] Config of php.ini updated")
		else:
        	        print ("\033[1;34;40m [CORRECT] - Hide display_errors is off in php.ini") 


	#Searching backup files in DocumentRoot directory!
	if (apache == True):
		#Search DocumentRoot directory
		print ("\033[1;37;40m [+] Checking for backup files in DocumentRoot directory...")
		cmd = os.popen("grep 'DocumentRoot' /etc/apache2/sites-enabled/* | awk '{{print $2}}'").read()
		if cmd:
			documentroot = cmd
			documentroot = documentroot[:-1]
			cmd = os.popen('find ' + documentroot + ' -type f -name  "*.bak" -o -name "*-DR" -o -name "*.back" -o -name "*.old" -o -name "*.OLD"').read()
			if cmd:
				print ("\033[1;31;40m A backup file found in:\n " + cmd)
			else:
				print ("\033[1;34;40m [CORRECT] - No backup files found in DocumentRoot")

	if (ssh == True):
		os.system("/etc/ssh/sshd_config /tmp/.sshd_config")
		cmd = os.popen('grep "Port 22"').read()
                if cmd:
			os.system("sed 's/Port 22/Port 40022/g' /etc/ssh/sshd_config")
			print ("\033[1;32;40m [PASS] - Changing default port of SSH (22) to 40022")
		else:
			print ("\033[1;34;40m [CORRECT] - SSH port is not a default port")


elif (dist[0] == "CentOS"):
	print ("Hola")
	#check apache and nginx.
	apache = os.path.exists('/etc/httpd/')

	if (apache == True):
		print ("\033[1;37;40m [+] Checking Apache...")	
		#Change ServerSignature
		cmd = os.popen('grep -R "ServerSignature On" /etc/httpd/conf/httpd.conf | grep -v "#" ').read()
		if cmd:
			os.system("grep -R 'ServerSignature On' /etc/httpd/conf/httpd.conf | grep -v '#' | cut -d':' -f 1 | xargs -i  sed -i 's/ServerSignature On/ServerSignature Off/g' {} ")
			print ("\033[1;32;40m [PASS] Changing ServerSignature On to Off")
		else:
			print ("\033[1;34;40m [CORRECT] - ServerSignature is Off")

		#Change ServerTokens
		cmd = os.popen('grep -R "ServerTokens OS" /etc/httpd/conf/httpd.conf | grep -v "#" | grep -v "Prod"').read()
		if cmd:
			os.system("grep -R 'ServerTokens' /etc/httpd/conf/httpd.conf | grep -v '#' | grep -v 'Prod' | cut -d':' -f 1 | xargs -i  sed -i 's/ServerTokens OS/ServerTokens Prod/g' {} ")
			print ("\033[1;32;40m [PASS] Changing ServerTokens to Prod for hide Apache version")
		else:
			print ("\033[1;34;40m [CORRECT] - ServerTokens value is Prod")

		#Change Options.
		cmd = os.popen('grep -R "Options None" /etc/httpd/conf/httpd.conf').read()
		if cmd:
			#Canviar la part del \n
			command = "grep -R 'Options' /etc/httpd/conf/httpd.conf | cut -d':' -f2 | xargs -I '{}' sed -i 's/Options None/Options -ExecCGI -Indexes -Includes/g' /etc/httpd/conf/httpd.conf"
			os.system(command)
			print ("\033[1;32;40m [PASS] Changing Options...")
		else:
			print ("\033[1;34;40m [CORRECT] - Options directive is correct!")



		os.system("systemctl restart httpd")
	
		print ("\033[1;37;40m [+] Installing mod_security and mod_evasive...")	
		os.system("yum install -y mod_security")
		os.system("yum install -y mod_evasive")
		os.system("systemctl restart httpd")
