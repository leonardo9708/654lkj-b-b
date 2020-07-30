
from uuid import getnode as get_mac
import os

#####MAC ADDRESS
newhostname = str(get_mac())
print(newhostname)

with open('/etc/hosts', 'r') as file:
        # read a list of lines into data
        data = file.readlines()

        # the host name is on the 6th line following the IP address
        # so this replaces that line with the new hostname
        data[5] = '127.0.1.1       ' + newhostname

        # save the file temporarily because /etc/hosts is protected
        with open('temp.txt', 'w') as file:
            file.writelines( data )

        # use sudo command to overwrite the protected file
        os.system('sudo mv temp.txt /etc/hosts')

        # repeat process with other file
        with open('/etc/hostname', 'r') as file:
            data = file.readlines()

        data[0] = newhostname

        with open('temp.txt', 'w') as file:
            file.writelines( data )

        os.system('sudo mv temp.txt /etc/hostname')
