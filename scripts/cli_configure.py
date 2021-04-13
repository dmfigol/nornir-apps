from nornir import InitNornir
from nornir_jinja2.plugins.tasks import template_file

# from nornir_napalm.plugins.tasks import napalm_configure
# from nornir_netmiko.tasks import netmiko_send_config
from nornir_scrapli.tasks import send_configs as scrapli_send_configs
from nornir_utils.plugins.functions import print_result


def configure_from_template(task):
    cfg = task.run(template_file, path="templates", template="config.j2").result
    # task.run(napalm_configure, configuration=cfg, replace=False)
    # task.run(netmiko_send_config, config_commands=cfg)
    task.run(scrapli_send_configs, configs=cfg.splitlines())


def main():
    with InitNornir(config_file="nr-config-local.yaml") as nr:
        result = nr.run(configure_from_template)
        print_result(result)


if __name__ == "__main__":
    main()
