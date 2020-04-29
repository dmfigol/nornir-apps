from nornir import InitNornir
from nornir.plugins.tasks.networking import netmiko_send_config, napalm_configure
from nornir.plugins.tasks.text import template_file
from nornir.plugins.functions.text import print_result

from nornir_scrapli.tasks import send_configs as scrapli_send_configs


def configure_from_template(task):
    cfg = task.run(
        template_file, path="templates", template="config.j2"
    ).result
    task.run(napalm_configure, configuration=cfg, replace=False)
    # task.run(netmiko_send_config, config_commands=cfg)
    # task.run(scrapli_send_configs, configs=cfg)


def main():
    with InitNornir(config_file="nr-config-local.yaml") as nr:
        result = nr.run(configure_from_template)
        print_result(result)


if __name__ == "__main__":
    main()
