from nornir import InitNornir
from nornir.plugins.tasks.networking import netconf_get_config
import xml.dom.minidom

def save_nc_get_config(task):
    with open(f"output/netconf/{task.host.name}.xml", "w") as f:
        result = task.run(task=netconf_get_config, source="running").result
        xml_pretty = xml.dom.minidom.parseString(result).toprettyxml()
        f.write(xml_pretty)


def main():
    with InitNornir(config_file="nr-config.yaml") as nr:
        results = nr.run(task=save_nc_get_config)
        # print_result(results)

if __name__ == '__main__':
    main()
