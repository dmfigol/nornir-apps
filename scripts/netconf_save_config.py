from pathlib import Path
import shutil

from nornir import InitNornir
from nornir_scrapli.tasks import netconf_get_config
from nornir_utils.plugins.functions import print_result

OUTPUT_DIR = Path("output/netconf")


def save_nc_get_config(task):
    with open(f"output/netconf/{task.host.name}.xml", "w") as f:
        cfg_xml = task.run(task=netconf_get_config, source="running").result
        f.write(cfg_xml)


def main():
    if OUTPUT_DIR.is_dir():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with InitNornir(config_file="nr-config-local.yaml") as nr:
        results = nr.run(task=save_nc_get_config)
        # print_result(results)


if __name__ == "__main__":
    main()
