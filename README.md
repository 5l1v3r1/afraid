# afraid
freedns.afraid.org DDNS client  

# Dependencies
pyreadline for windows only.
Install with pip:
		pip install pyreadline  

# Usage
		add <username> 		- Add a new account to the DB.
		ls 					- List all domains and corresponding ip's.
		maintain <domains> 	- Keep domains up to date with current ip.
		release <domains> 	- Stop updating domains with current ip.
		<domain> <ip> 		- Point domain at IP, current IP is used if left blank.
		timeout <seconds> 	- Set the interval between IP checks for maintain command.
		refresh 			- Update local DB.'