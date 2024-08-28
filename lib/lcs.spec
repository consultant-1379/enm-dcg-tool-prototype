#####
# Spec file for lcs
#####

%define name lcs
%define pwd %(pwd)
%define src /root/enm-dcg-tool-prototype
%define version 1.16
%define release PA1
%define arch noarch
#%define dependency bash, pexpect, python >= 2.6, python < 3, python-yaml >= 3.10, wget >= 1.12
%define dependency bash, python >= 2.6, python < 3, python-yaml >= 3.10

# To where the files should be saved
%define prefix /opt/ericsson/lcs

# The (base) name of the package, which should match the SPEC file name
Name: %{name}

# The upstream version number of the software.
Version: %{version}

# The initial value should normally be 1%{?dist}, this value should be incremented each new release of the package and reset to 1 when a new Version of the software is built.
Release: %{release}

# A brief, one-line summary of the package.
Summary: LCS

# The license of the software being packaged. For packages that are destined for community distributions such as Fedora this must be an Open Source License abiding by the specific distribution’s Licensing Guidelines.
License: (c) Ericsson

# The full URL for more information about the program (most often this is the upstream project website for the software being packaged).
URL: www.ericsson.com

# If the package is not architecture dependent, i.e. written entirely in an interpreted programming language, this should be BuildArch: noarch otherwise it will automatically inherit the Architecture of the machine it’s being built on.
BuildArch: %{arch}

# A comma or whitespace separated list of packages required by the software to run once installed. There can be multiple entries of Requires each on its own line in the SPEC file.
Requires: %{dependency}

AutoReqProv: no


%description
LCS

#####
# Preparation phase
#####
%prep
#!/bin/sh
if [ ! -z ${RPM_BUILD_DIR} ]; then
    sudo rm -rf ${RPM_BUILD_DIR}/*
fi
if [ ! -z ${RPM_BUILD_ROOT} ]; then
    sudo rm -rf ${RPM_BUILD_ROOT}/*
fi
mkdir -p ${RPM_BUILD_ROOT}/%{prefix}
cd %{src}
sudo tar --exclude='*.pyo' --exclude='*.pyc' --exclude='*/.git*' --exclude='*/.idea*' --exclude='lcs.spec' --exclude='*delete_me*' -cpf - . | tar -C ${RPM_BUILD_ROOT}/%{prefix} -xvf -
cd ${RPM_BUILD_ROOT}
find -L .%{prefix} -depth -print | sed -e 's/^\.//' -e 's/.*/"\0"/' > ${RPM_BUILD_DIR}/lcs_files

#####
# Clean-up phase
#####
%clean
if [ ! -z ${RPM_BUILD_DIR} ]; then
    sudo rm -rf ${RPM_BUILD_DIR}/*
fi
if [ ! -z ${RPM_BUILD_ROOT} ]; then
    sudo rm -rf ${RPM_BUILD_ROOT}/*
fi

#####
# Pre-installation phase
#####
%pre

#####
# Post-installation phase
#####
%post
#!/bin/sh
if [[ ! -f /ericsson/tor/data/global.properties ]]; then
    FILE_LIST=($(find /opt/ericsson/lcs/lib -type f -exec grep -il 'pexpect' {} \;))
    for file in $(echo ${FILE_LIST[@]}); do perl -pi -e "s|import pexpect||g" $file; done
fi
chmod 755 /opt/ericsson/lcs/bin/*.bsh
if [[ -f /ericsson/tor/data/global.properties ]]; then
    echo -e 'Log Collection Service tool was installed successfully.\nPlease set up the tool by running the command:\nbash /opt/ericsson/lcs/bin/log_collection.bsh --setup' > /dev/stdout
fi

#####
# Pre-uninstallation phase
#####
%preun

#####
# Post-uninstallation phase
#####
%postun
if [ "$1" == "0" ];then
    sudo rm -rf %{prefix}
    # Prompt message telling the user that the tool has been uninstalled
    echo 'Log Collection Service tool was uninstalled successfully.' > /dev/stdout
elif [ "$1" == "1" ];then
    echo 'Log Collection Service tool is being upgraded' > /dev/stdout
    diff /root/.origin_lcs.conf /opt/ericsson/lcs/etc/.origin_lcs.conf >/dev/null
    if [ echo $? == "0" ];then
        echo "upgrading"
    else
        echo "Detecting new parameters in lcs.conf please run --setup to implement these changes' >> /opt/ericsson/lcs/etc/.upgrade c"
    fi
fi


#####
# Files included in package
#####
%files -f lcs_files
