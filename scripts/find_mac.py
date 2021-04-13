from nornir import InitNornir
from nornir_scrapli.tasks import send_command as scrapli_send_command
from nornir_utils.plugins.functions import print_result
from nornir.core.filter import F
from nornir.core.task import Result

from collections import ChainMap
from typing import List, Dict, Any, Tuple, NamedTuple, Set

from nr_app.utils import normalize_interface_name


class ResultInterface(NamedTuple):
    device_name: str
    int_name: str
    belongs: bool


def build_mac_to_int_mapping(
    parsed_data: List[Dict[str, str]], device_name: str
) -> Dict[str, ResultInterface]:
    """
    Returns:
        dictionary with mac address as key in the format 5254.001b.091c
    """
    result: Dict[str, ResultInterface] = {}
    for int_data in parsed_data:
        mac = int_data.get("address")
        int_name = int_data.get("interface")
        if mac and int_name:
            interface = ResultInterface(
                device_name=device_name, int_name=int_name, belongs=True
            )
            result[mac] = interface
    return result


def build_mac_to_int_mapping_task(task):
    nr_result = task.run(scrapli_send_command, command="show interface")
    parsed_data = nr_result.scrapli_response.textfsm_parse_output()
    task.host["mac_to_int"] = build_mac_to_int_mapping(parsed_data, task.host.name)
    # return Result(host=task.host, result=parsed_data)


def get_access_ports_from_int_sw_data(parsed_data: List[Dict[str, str]]) -> Set[str]:
    result = set()
    for int_data in parsed_data:
        if int_data["mode"] == "static access":
            int_name = normalize_interface_name(int_data["interface"])
            result.add(int_name)
    return result


def mac_to_int_from_mac_addr_table(
    parsed_data: List[Dict[str, str]], access_ports: Set[str], device_name: str
) -> Dict[str, ResultInterface]:
    result: Dict[str, ResultInterface] = {}
    for mac_data in parsed_data:
        interface_name = normalize_interface_name(mac_data["destination_port"])
        if interface_name in access_ports:
            mac_addr = mac_data["destination_address"]
            result[mac_addr] = ResultInterface(
                device_name=device_name, int_name=interface_name, belongs=False
            )
    return result


def gather_connected_macs(task):
    int_sw_nr_result = task.run(
        scrapli_send_command, command="show interface switchport"
    )
    parsed_int_sw_data = int_sw_nr_result.scrapli_response.textfsm_parse_output()

    access_ports = get_access_ports_from_int_sw_data(parsed_int_sw_data)
    # breakpoint()
    mac_addr_table_result = task.run(
        scrapli_send_command, command="show mac address-table"
    )
    parsed_mac_addr_table = (
        mac_addr_table_result.scrapli_response.textfsm_parse_output()
    )
    mac_to_int = mac_to_int_from_mac_addr_table(
        parsed_mac_addr_table, access_ports, device_name=task.host.name
    )
    task.host["mac_to_int"].update(mac_to_int)


def gather_all_macs() -> Dict[str, ResultInterface]:
    nr = InitNornir(config_file="inventories/simple-topology/nr-config.yaml")
    iosv = nr.filter(F(groups__contains="iosv"))
    all_ios_devices = nr.filter(F(groups__any=["iosv", "csr"]))
    all_ios_devices.run(build_mac_to_int_mapping_task)

    results = iosv.run(gather_connected_macs)
    print_result(results)

    mac_to_interface = {}
    for host in all_ios_devices.inventory.hosts.values():
        mac_to_interface.update(host["mac_to_int"])
    return mac_to_interface


def main():
    """This scripts is looking for the location of MACs on the network.
    It might need some additional work for an arbitrary network"""
    mac = "5254.001b.d37b"
    mac = "5254.0003.9b4c"
    mac_to_interface = gather_all_macs()

    interface = mac_to_interface.get(mac)
    if interface is None:
        print(f"Mac {mac} was not found")
    elif interface.belongs:
        print(
            f"Interface {interface.int_name} on device {interface.device_name} has mac {mac}"
        )
    elif not interface.belongs:
        print(
            f"A client with mac {mac} is connected to {interface.device_name}.{interface.int_name}"
        )


if __name__ == "__main__":
    main()


# mac -> (device, interface)
