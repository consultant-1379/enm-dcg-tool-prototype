#!/usr/bin/python
# ********************************************************************
# Ericsson LMI                                    SCRIPT
# ********************************************************************
#
# (c) Ericsson LMI 2018 - All rights reserved.
#
# The copyright to the computer program(s) herein is the property
# of Ericsson LMI. The programs may be used and/or copied only with
# the written permission from Ericsson LMI or in accordance with the
# terms and conditions stipulated in the agreement/contract under
# which the program(s) have been supplied.
#
# ********************************************************************
# Name          : lcs_main.py
# Purpose       : Automated Data Collection
# Documentation :
#   https://confluence-nam.lmera.ericsson.se/pages/viewpage.action?spaceKey=ENMCOP&title=Automated+Data+Collection
# Date          : 20 Nov 2018
# ********************************************************************
#
# To generate the installer .rpm file.
# 1. Install required packages by executing the command:
#       yum install gcc rpm-build rpm-devel rpmlint make python bash coreutils diffutils patch rpmdevtools
# 2. copy the directory enm-lcs-tool-prototype to /root/
# 3. Make sure the lcs.spec file is in LF format, execute the command:
#       sed -e "s/\r//g" -i /root/enm-lcs-tool-prototype/lcs.spec
# 4. execute the command to generate the .rpm installer: rpmbuild -bb /root/enm-lcs-tool-prototype/dcg.spec
# To install or uninstall .rpm package
# 1. rpm -ivh /root/rpmbuild/RPMS/noarch/lcs-1.0-PA1.noarch.rpm
# 2. rpm -e lcs
# ********************************************************************

import os
import sys

py_command_components = list()

# Add the interpreter
py_command_components.append("python")

argv = sys.argv

# Current python file path
path = os.path.realpath(argv[0])

# Current python file directory
directory = os.path.dirname(path)

lcs_directory = os.path.abspath(os.path.join(directory, os.pardir))
script_relative_path = "lib/lcs_main.py"

# The LCS main Python script to be executed
script_path = os.path.join(lcs_directory, script_relative_path)
py_command_components.append(script_path)

# Add the current file path as the first argument
py_command_components.append(path)

# Add user arguments
py_command_components += argv[1:]

# command to be executed
command = " ".join(py_command_components)

# Execute the command
os.system(command)
