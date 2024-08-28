"""
This file stores non-configurable variables
"""
from libs.variables.configuration import Configuration
from libs.variables.keys import MenuKeys

tool_description = r""""""

version_info = r"""
Log Collection Service 1.1
(c) Ericsson LMI 2018 - All rights reserved.
"""

exit = {MenuKeys.item_name: "Exit", MenuKeys.config_file: Configuration.previous_menu}
go_back = {MenuKeys.item_name: "Previous Menu", MenuKeys.config_file: Configuration.previous_menu}
finish_review = {MenuKeys.item_name: "Finish and Review", MenuKeys.config_file: Configuration.finish_review}

separator = '*' * 60

lcs_conf_file_name = "lcs.conf"
config_dir = "etc"

# default value JBoss log file paths (list<string>)
JBoss_logs = ["/ericsson/3pp/jboss/standalone/log/server.log"]


default_debug_time = 300  # 5 minutes

