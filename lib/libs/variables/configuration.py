class Configuration(object):
    # Configured Variables     This variable will be set according to the .conf file
    #############################################################################################################
    default_main_file = None
    default_path = None
    configuration_dir = None
    lcs_conf_path = None

    # When DEBUG = True, all commands will be print out before execution
    verbose = False

    #############################################################################################################
    # physical server or cloud server
    cloud_server = False
    #############################################################################################################
    # This specifies if the user wishes to unmount the output directory after every execution (True/False)
    report_mount_umount = False

    # the program finally Zips the files in "storing_logs_dir" and stores the finally report in this directory
    report_output_dir = None
    report_output_dir_response = False

    # A mounted directory that the program stores log files temporarily
    storing_logs_dir = None

    # The host file that lists all available cluster server (for physical server only).
    hosts_file_name = "/etc/hosts"
    scripts_file_path = None

    # Retrieves the ENM version from the physical server.
    physical_server_enm_version = '/opt/ericsson/enminst/bin/enm_version.sh'

    # Retrieves the ENM version from the cloud server.
    cloud_server_enm_version = 'consul kv get "enm/deployment/enm_version"'

    # The startup file inside the <config_files_dir> directory.
    start_up_file = None
    # The file the tool is currently executing
    log_trigger = True
    # The directory of the configuration files.
    config_files_dir = None

    dont_display = False

    vm_user_name = None
    # Port number to login to virtual machines (cluster server).
    vm_port_number = 22
    vm_private_key = None
    temp_key = None
    vm_password = None
    #############################################
    # options
    last_run_file_time = None
    manual_actions = False
    jboss_debug = True
    JBoss_loggers = None
    JBoss_plug_in_output_dir = None
    JBoss_time_out = None
    JBoss_log_path = None
    jboss_is_running = None
    failed_Jboss_diabled_list = []
    plugin_count = 0
    JBoss_ans_true = None
    Jboss_log_not_collected = None
    JBoss_maximum_time = None
    time_stamp_jboss = None
    setup = None
    jboss_plug_timeout = 300

    # Pre-set variables     Set this variable in this file
    #############################################################################################################
    # File system
    directory_to_check_disk_usage = "/ericsson/enm/dumps"
    file_system_max_usage = None
    #############################################################################################################
    exit_code_when_error_occurs = 1
    select_all = "select all"
    finish_review = "finish and review"
    previous_menu = "previous menu"
    current_menu = "current menu"
    debug_time = None

    setup_detail_file = None

    database_file = None

    database_table = 'CREDENTIALS'
    #############################################################################################################
    # Additional files
    skip_additional_config_file = None
    #############################################################################################################
    # credentials to log into peer_servers
    peer_server_username = None
    peer_server_password = None
    peer_server_root_password = None
    peer_server_command_timeout = None

    # Number of old copies of data
    max_number_of_reports = None
    max_file_size = None

    #############################################################################################################
    # DDC data file variables
    DDC_time_out = None
    DDC_output_dir = None
    DDC_collection = None
    #############################################################################################################
    # Logging
    tag_name = 'LogCollectionService'
    log_file_location = None
    #############################################################################################################
    # Cli Plugin
    cli_username = None
    cli_password = None
    cli_role = None
    cli_correct_vm = None
    cli_blank = None
    cli_timeout = None
    cli_status = None
    JOB_ID_RETURN = None
    enm_cli_dont_display = None
    executing_username = None
    executing_password = None
    executing_role = None
    enm_cli_check = False
    enm_username_check = None
    enm_cli_pass_usr_wrong = None
    #############################################################################################################
    # tcp
    TCP_collection = None
    tcptaring = False
    jboss_command_stamp = None
    #############################################################################################################
    # execution time
    start_time = None
    end_time = None
    #############################################################################################################
    # command line vm entry
    vm_name = False
    #############################################################################################################
    # dynamic menu
    dynamic_menu = None
    dynamic_menu_path = None
    menu_run_file = None
    return_to_menu_page = None
    page_num = None
    first = False
    menu_next_list = []
    #############################################################################################################
    exclude_file_paths = None
    exclude_file_extensions = None

    JID_ID = None
    JID_present = None
    JID_path = None
    #############################################################################################################
    # ftp server
    ftp_silent_setup = None
    url_check = None
    ftp_url = None
    ftp_username = None
    ftp_password = None
    ftp_no_upload = None
    upload_choice = None
    # specifies if you want to delete trouble report after upload
    Delete_file_after_upload = None
    Automatic_upload = None
    #############################################################################################################
    # silent setup
    silent_setup = None
    #############################################################################################################
    # ticket number
    ticket_number = None
    ticket_dir = None
    #############################################################################################################
    # Auto clean up of report_output_dir
    Auto_clean = None
    Duration = None
    #############################################################################################################
    execute_multiple_files = None
    use_tool_while_instance_running = None
    #############################################################################################################
    yes_to_all = False
    #############################################################################################################
    # Network Element Dynamic Menu variables
    network_element_path = "NETWORK_ELEMENTS"
    network_element_filename = ".autoexec.yml"
    network_element_output = None
    netlog_collection_timeout = None
    displaying_net_sim = None
    netsim_page_num = 1
    #############################################################################################################
    # manual for endyamlfile
    manual_endYamlFile = None
    manual_startYamlFile = None
    tmp_directory = None
    #############################################################################################################
    # DDP url
    DDP_URL = None
    DDP_URL_WRONG = None
    #############################################################################################################
    # EOCM Flag
    Jboss_EOCM = None
    EOCM = None
    username = None
    #############################################################################################################
    # fix for noe4j
    neo4j_fix = None
