import subprocess

from libs.utilities.system.terminal import Terminal
from libs.variables.configuration import Configuration


class GlobalSearch():

    def __init__(self, instances):
        self.instances = instances
        self.list1 = list1 = []
        self.list2 = list2 = []

        # if string convert to list of string
        if type(instances) == str:
            variable = instances
            instances = [variable]

        if type(instances) == list:
            for each_instance in instances:
                instance_index = False
                if Configuration.cloud_server is True and 'neo4j' in str(each_instance):
                    get_ips = "consul members | grep " + each_instance + " | awk '{print $2}' | awk -F ':' '{print $1}'"
                    Configuration.neo4j_fix = True
                else:
                    if str(each_instance).count("-") == 1:
                        value = each_instance.partition("-")[0]
                        instance_index = each_instance.partition("-")[2]
                        try:
                            instance_index = int(instance_index) - 1
                        except ValueError:
                            list2.append(each_instance)
                            continue
                        # if Configuration.cloud_server is False:
                        get_ips = "[[ -f /ericsson/tor/data/global.properties ]] && egrep '^" + value + "=' /ericsson/tor/data/global.properties"
                        # else:
                        #     get_ips = "egrep '^" + value + "=' /var/tmp/.lcs_gp/global.properties"
                    else:
                        # if Configuration.cloud_server is False:
                        get_ips = "[[ -f /ericsson/tor/data/global.properties ]] && egrep '^" + each_instance + "=' /ericsson/tor/data/global.properties"
                        # else:
                        #     get_ips = "egrep '^" + each_instance + "=' /var/tmp/.lcs_gp/global.properties"
                pipe = subprocess.Popen(get_ips, shell=True, stdout=subprocess.PIPE).stdout
                pipe_read = pipe.read()
                pipe.close()
                if Configuration.neo4j_fix is True and pipe_read is not '':
                    Configuration.neo4j_fix = False
                    list_vm = pipe_read.split('\n')
                    string = str(list_vm).replace('[', '').replace(']', '').replace("'", '').strip()
                    check_pipe = each_instance + '=' + string
                else:
                    check_pipe = pipe_read
                if check_pipe is None or check_pipe == "":
                    list2.append(each_instance)
                else:
                    ip_string = str(check_pipe).strip()
                    ip_string = ip_string.partition("=")[2]
                    if ip_string.count(",") > 0:
                        ip_string = ip_string.split(",")
                        list_of_ip = list(ip_string)
                    else:
                        list_of_ip = [ip_string]
                    if type(instance_index) is int:
                        try:
                            ip_check = list_of_ip.__getitem__(instance_index)
                            if ip_check is not '':
                                get_instance_command = "getent hosts " + ip_check + " | awk {'print $2'}"
                                pipe2 = subprocess.Popen(get_instance_command, shell=True, stdout=subprocess.PIPE).stdout
                                check_pipe = pipe2.read()
                                check_pipe = str(check_pipe).strip()
                                pipe2.close()
                                if check_pipe is not None:
                                    list1.append(check_pipe)
                                else:
                                    list2.append(each_instance)
                        except IndexError:
                            list2.append(each_instance)
                            continue
                    elif instance_index is False:
                        for each_ip in list_of_ip:
                            if each_ip is not '':
                                get_instance_command = "getent hosts " + each_ip + " | awk {'print $2'}"
                                pipe2 = subprocess.Popen(get_instance_command, shell=True, stdout=subprocess.PIPE).stdout
                                check_pipe = pipe2.read()
                                check_pipe = str(check_pipe).strip()
                                pipe2.close()
                                list1.append(check_pipe)

        self.list1 = self.remove_duplicates(list1)
        self.list2 = self.remove_duplicates(list2)
        for each in self.list1:
            if self.ping_server(each) is False:
                self.list1.remove(each)
                self.list2.append(each)

    @staticmethod
    def remove_duplicates(list):
        unique = []
        for elem in list:
            if elem not in unique:
                unique.append(elem)

            # Return the list of unique elements
        return unique

    @staticmethod
    def ping_server(server):
        """
        :param server:
        :return:
        """
        reply = Terminal.system("ping -c 1 " + server + " > /dev/null 2>&1")
        if reply == 0:
            return True
        else:
            return False

    def get_correct_list(self):
        return self.list1

    def get_incorrect_list(self):
        return self.list2
