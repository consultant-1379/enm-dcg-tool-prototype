class BasicKeys(object):
    config_name = "config_name"
    config_type = "config_type"
    current_file_path = 'current_file_path'
    next_config_type = 'next_config_type'
    file_type = 'file_type'


class AppKeys(object):
    functions = "functions"
    func_name = "func_name"
    implicit_plugins = 'implicit_plugins'

    #########################################
    # JBOSS

    # the instances key that specified in YAML file
    instances = "instances"

    # a single vm instance for internal use
    instance = "instance"

    JBoss_servers = "JBoss_servers"
    servers = 'servers'

    jboss_commands = 'Jboss_commands'
    run_command = 'run_commands'
    command_options = "commands"

    loggers = "loggers"
    file_handlers = 'file_handlers'

    level_value = 'log_level'

    log_file_paths = 'log_file_paths'
    debug_time = "timeout"

    #########################################
    # Execute Additional Config File
    additional_config_file_path = 'additional_config_file_path'
    storing_log = 'storing_log'

    #########################################
    # wait
    message = 'message'

    #########################################
    # Collect Files
    files = 'files'
    global_exclusion_files = "global_files"
    global_exclusion_ext = "global_extensions"
    #########################################
    # Manual Actions

    action_title = 'action_title'
    actions = 'actions'

    action_list = 'action_list'

    #########################################
    # Commands
    server_type = 'server_type'
    commands = 'execute_commands'
    sudo = 'sudo'
    func_log_dir = "func_log_dir"
    #########################################
    # ENM CLI
    enm_commands = 'enm_commands'
    enm_role = 'enm_role'
    check_status = 'check_status'
    timeout = 'timeout'
    #########################################
    # Collect Old Image
    log_path = "log_path"
    vm_list = "vm_list"
    image_age = "image_age"
    #########################################


class MenuKeys(object):
    item_name = "item_name"
    options = "options"
    config_file = "config_file"
    title = "title"

    menu_type = 'menu_type'

    redisplay = 'redisplay'


class JBossMenuKeys(object):
    options_type = 'options_type'
    selected = 'selected'
