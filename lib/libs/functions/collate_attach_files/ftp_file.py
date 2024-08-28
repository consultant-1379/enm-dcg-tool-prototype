import os
from ftplib import FTP
from libs.utilities.system.output import Output
from libs.utilities.system.terminal import Terminal
from libs.variables.configuration import Configuration


class FtpFiles:

    def __init__(self, report_gz_file_name):
        self.report_gz_file_name = report_gz_file_name
        if Configuration.ticket_number is True:
            self.ticket_dir = str(Configuration.ticket_dir[0])

    def run(self):
        try:
            # check if connection established
            ftp = FTP()
            ftp.connect(str(Configuration.ftp_url))
            ftp.login(Configuration.ftp_username, Configuration.ftp_password)
        except:
            Output.red('An Error Occured when trying to connect to %s server, username or password is incorrect'
                       % Configuration.ftp_url)
            return False

        if os.path.exists(self.report_gz_file_name) is True:
            try:
                resp = ftp.sendcmd('MLST lcs_reports')
                # check if lcs_report directory exists
                if 'type=dir;' in resp:
                    # if it exists cd into it
                    ftp.cwd('lcs_reports')
                    try:
                        # check if hostname directory exists
                        resp = ftp.sendcmd('MLST ' + Terminal.hostname())
                        if 'type=dir;' in resp:
                            # if it exists cd into it
                            ftp.cwd(Terminal.hostname())
                            # check if ticket has been selected
                            try:
                                if Configuration.ticket_number is True:
                                    # check if directory exists
                                    try:
                                        resp = ftp.sendcmd('MLST ' + self.ticket_dir)
                                        if 'type=dir;' in resp:
                                            # cd into directory
                                            ftp.cwd(self.ticket_dir)
                                            # store the file on server
                                            log_file = open(self.report_gz_file_name, 'rb')
                                            ftp.storbinary('STOR ' + os.path.basename(self.report_gz_file_name),
                                                           log_file)
                                            ftp.quit()
                                            return True
                                    except:
                                        # make the directory
                                        ftp.mkd(self.ticket_dir)
                                        # cd into directory
                                        ftp.cwd(self.ticket_dir)
                                        # store the file on server
                                        log_file = open(self.report_gz_file_name, 'rb')
                                        ftp.storbinary('STOR ' + os.path.basename(self.report_gz_file_name), log_file)
                                        ftp.quit()
                                        return True
                                else:
                                    log_file = open(self.report_gz_file_name, 'rb')
                                    ftp.storbinary('STOR ' + os.path.basename(self.report_gz_file_name), log_file)
                                    ftp.quit()
                                    return True
                            except:
                                Output.red("Can't make %s directory on ftp server" % self.ticket_dir)
                                return False
                    except:
                        # make hostname directory
                        ftp.mkd(Terminal.hostname())
                        # cd into directory
                        ftp.cwd(Terminal.hostname())
                        try:
                            if Configuration.ticket_number == True:
                                # make the directory
                                ftp.mkd(self.ticket_dir)
                                # cd into directory
                                ftp.cwd(self.ticket_dir)
                                # store the file
                                log_file = open(self.report_gz_file_name, 'rb')
                                ftp.storbinary('STOR ' + os.path.basename(self.report_gz_file_name), log_file)
                                ftp.quit()
                                return True
                            else:
                                # store the file
                                log_file = open(self.report_gz_file_name, 'rb')
                                ftp.storbinary('STOR ' + os.path.basename(self.report_gz_file_name), log_file)
                                ftp.quit()
                                return True
                        except:
                            Output.red("Can't make %s directory on ftp server after making %s directory"%(self.ticket_dir,Terminal.hostname()))
                            return False
                else:
                    try:
                        # Make the directory
                        ftp.mkd('lcs_reports')
                        ftp.cwd('lcs_reports')
                        ftp.mkd(Terminal.hostname())
                        ftp.cwd(Terminal.hostname())
                        if Configuration.ticket_number is True:
                            ftp.mkd(self.ticket_dir)
                            ftp.cwd(self.ticket_dir)
                            log_file = open(self.report_gz_file_name, 'rb')
                            ftp.storbinary('STOR ' + os.path.basename(self.report_gz_file_name), log_file)
                            ftp.quit()
                            return True
                        else:
                            log_file = open(self.report_gz_file_name, 'rb')
                            ftp.storbinary('STOR ' + os.path.basename(self.report_gz_file_name), log_file)
                            ftp.quit()
                            return True
                    except:
                        Output.red("Cannot create lcs_reports directory on %s server" % Configuration.ftp_url)
                        return False
            except:
                Output.red('Problem with ftp server')
        else:
            Output.red("Trouble report %s can not be found" % self.report_gz_file_name)
            return False
