from typing import Dict, Any, Optional, Union

from lxml import etree


def extract_hostname_from_fqdn(fqdn: str) -> str:
    """Extracts hostname from fqdn-like string
    
    For example, R1.cisco.com -> R1,  sw1 -> sw1"
    """
    return fqdn.split(".")[0]


# def parse_show_cdp_neighbors(cli_output: str) -> Dict[str, Dict[str, str]]:
#     """Parses `show cdp neighbors` and returns a dictionary of neighbors and connected interfaces"""
#     result: Dict[str, Dict[str, str]] = {}
#     for neighbor_output in NEIGHBOR_SPLIT_RE.split(cli_output):
#         match = CDP_NEIGHBOR_RE.search(neighbor_output)
#         if match:
#             remote_fqdn = match.group("remote_fqdn")
#             local_interface = normalize_interface_name(match.group("local_interface"))
#             remote_interface = normalize_interface_name(match.group("remote_interface"))
#             remote_hostname = extract_hostname_from_fqdn(remote_fqdn)
#             result[local_interface] = {
#                 "connected_device": {
#                     "name": remote_hostname,
#                     "port": remote_interface,
#                 }
#             }
#     return dict(sorted(result.items()))


def dict_to_xml(data: Any, root: Union[None, str, etree.Element] = None, attr_marker: str = '_') -> etree.Element:
    def _dict_to_xml(data_: Any, parent: Optional[etree.Element] = None) -> None:
        nonlocal root
        if not isinstance(data_, dict):
            raise ValueError("provided data must be a dictionary")

        for key, value in data_.items():
            if key.startswith(attr_marker):
                # handle keys starting with attr_marker as tag attributes
                attr_name = key.lstrip(attr_marker)
                parent.attrib[attr_name] = value
            else:
                element = etree.Element(key)
                if root is None:
                    root = element

                if parent is not None and not isinstance(value, list):
                    parent.append(element)

                if isinstance(value, dict):
                    _dict_to_xml(value, element)
                elif isinstance(value, list):
                    for item in value:
                        list_key = etree.Element(key)
                        parent.append(list_key)
                        _dict_to_xml(item, list_key)
                else:
                    if value is not None and not isinstance(value, str):
                        value = str(value)
                    element.text = value

    if isinstance(root, str):
        root = etree.Element(root)
    _dict_to_xml(data, root)
    return root
