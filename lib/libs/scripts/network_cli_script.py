# !/usr/bin/python
import enmscripting, sys

check_status = sys.argv[1]
timeout = sys.argv[2]
nr_of_logs = None
id = None
int_t = None

try:
    int_t = int(timeout)
except ValueError:
    pass

commands = list()

session = enmscripting.open()

if str(check_status) == "None" or check_status is None:
    for each in sys.argv[3:]:
        commands.append(each)

    for each in commands:
        print "\n\nNetwork Cli Commands \tCLI Timeout: %s \tCLI Check Status: %s \tCLI Command: %s\n\n" %\
              (timeout, check_status, each)
        terminal = session.terminal()
        response = terminal.execute(each)
        for line in response.get_output():
            print line
else:
    nr_of_logs = sys.argv[3]
    can_collect = None
    try:
        nr_of_logs = int(nr_of_logs)
    except ValueError:
        pass

    for each in sys.argv[4:]:
        commands.append(each)

    for each in commands:
        print "\n\nNetwork Cli Commands \tCLI Timeout: %s \tCLI Check Status: %s \tCLI Command: %s\n\n" % \
              (timeout, check_status, each)
        terminal = session.terminal()
        response = terminal.execute(each)
        c = 0
        for line in response.get_output():
            print line
            if str(line).__contains__("successfully started"):
                c = c + 1
        if c != nr_of_logs:
            can_collect = c
            print "Not all logs started upload successfully"

        import time
        timeout = None
        check = False
        if int_t is not None:
            timeout = time.time() + (60*int_t)
        start_time = time.time()
        while check is False:
            count = 0
            terminal = session.terminal()
            response = terminal.execute(check_status)
            for line in response.get_output():
                if str(line).__contains__("READY_FOR_DOWNLOAD"):
                    count = count + 1
            if can_collect is None:
                if count == nr_of_logs:
                    for line in response.get_output():
                        print line
                    print "All logs ready for download"
                    check = True
            else:
                if count == can_collect:
                    for line in response.get_output():
                        print line
                    print "Some logs ready for download"
                    check = True
            if timeout is not None:
                if time.time() > timeout:
                    for line in response.get_output():
                        print line
                    print "Timeout occurred after %s seconds" % (60*int_t)
                    check = True
            time.sleep(8)

enmscripting.close(session)