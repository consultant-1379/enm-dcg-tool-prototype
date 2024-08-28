# !/usr/bin/python
import enmscripting, sys

check_status = sys.argv[3]
timeout = sys.argv[4]
id = None
int_t = None

try:
    int_t = int(timeout)
except ValueError:
    pass

commands = list()
for each in sys.argv[6:]:
    commands.append(each)

session = enmscripting.open()
for each in commands:
    print "\n\nCLI UserName: %s \tCLI Role: %s \tCLI Timeout: %s \tCLI Command: %s\n\n" % \
          (str(sys.argv[1]), str(sys.argv[2]), str(sys.argv[4]), str(each))
    terminal = session.terminal()
    response = terminal.execute(each)
    for line in response.get_output():
        if str(check_status) != "None" and str(sys.argv[5]) == "True":
            id = line.split("ID")[1].strip()
            if str(check_status).__contains__("$$JID$$"):
                check_status = str(check_status).replace("$$JID$$", id)
        print(line)

if id != None:
    import time
    timeout = None
    check = False
    if int_t is not None:
        timeout = time.time() + int_t
    start_time = time.time()
    while check is False:
        terminal = session.terminal()
        response = terminal.execute(check_status)
        for line in response.get_output():
            if str(line).__contains__("COMPLETED"):
                check = True
        if timeout is not None:
            if time.time() > timeout:
                check = True

enmscripting.close(session)
