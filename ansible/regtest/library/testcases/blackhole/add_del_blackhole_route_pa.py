import shlex
from ansible.module_utils.basic import AnsibleModule
from collections import OrderedDict

HASH_DICT = OrderedDict()

def run_cli(module, cli):
    """
    Method to execute the cli command on the target node(s) and
    returns the output.
    :param module: The Ansible module to fetch input parameters.
    :param cli: The complete cli string to be executed on the target node(s).
    :return: Output/Error or None depending upon the response from cli.
    """
    cli = shlex.split(cli)
    rc, out, err = module.run_command(cli)

    if out:
        return out.rstrip()
    elif err:
        return err.rstrip()
    else:
        return None

def execute_commands(module, cmd):
    """
    Method to execute given commands and return the output.
    :param module: The Ansible module to fetch input parameters.
    :param cmd: Command to execute.
    :return: Output of the commands.
    """
    global HASH_DICT

    if ('service' in cmd and 'restart' in cmd) or module.params['dry_run_mode']:
        out = None
    else:
        out = run_cli(module, cmd)

    # Store command prefixed with exec time as key and
    # command output as value in the hash dictionary
    exec_time = run_cli(module, 'date +%Y%m%d%T')
    key = '{0} {1} {2}'.format(module.params['switch_name'], exec_time, cmd)
    HASH_DICT[key] = out

    return out


def add_del_blackhole(module):
    """
     Method to execute and verify port links.
     :param module: The Ansible module to fetch input parameters.
    """
    eth_list = module.params['eth_list'].split(',')

    if module.params['delete']:
        for eth in eth_list:
            ip = '10.0.{}.0/24'.format(eth)
            execute_commands(module, 'ip route delete {}'.format(ip))
            
    else:
        for eth in eth_list:
            ip = '10.0.{}.0/24'.format(eth)
            execute_commands(module, 'ip route add blackhole {}'.format(ip))

def main():
    """ This section is for arguments parsing """
    module = AnsibleModule(
        argument_spec=dict(
            delete=dict(required=False, type='bool', default=False),
            switch_name=dict(required=False, type='str'), 
            dry_run_mode=dict(required=False, type='bool', default=False),
            log_dir_path = dict(required=False, type='str'),
            hash_name=dict(required=False, type='str'),
            eth_list = dict(required=False, type='str', default='')
        )
    )

    add_del_blackhole(module)

    # Create a log file
    log_file_path = module.params['log_dir_path']
    log_file_path += '/{}.log'.format(module.params['hash_name'])
    log_file = open(log_file_path, 'a')
    for key, value in HASH_DICT.iteritems():
        log_file.write(key)
        log_file.write('\n')
        log_file.write(str(value))
        log_file.write('\n')
        log_file.write('\n')

    log_file.close()

    # Exit the module and return the required JSON.
    module.exit_json(
        hash_dict=HASH_DICT,
        log_file_path=log_file_path
    )


if __name__ == '__main__':
    main()
