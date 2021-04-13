## Repository with examples of Nornir applications
#### Supporting my DEVNET-2192 Automate your Network with Nornir presentation.

To run these examples, you need an environment with IOS-XE routers. You can have any number, but at least two is recommended. You would also want to modify the inventory folder with the details for your environment (IP addresses, credentials).  

On the control machine, you need to have Python 3.6+ installed (tested on Python 3.9.4). Dependencies are managed with [poetry](https://python-poetry.org/). After cloning the repository, use `poetry install` to install dependencies. When you are running the scripts, you would want to prepend them with `poetry run`, for example: `poetry run python scripts/gather_commands.py`. Run scripts in the root of the repository. 

#### License
It is MIT licensed. Feel free to do whatever you want with the code (including commercial use). No attribution is required.

#### Scripts details
* `gather_commands.py` - executes some show commands and saves outputs to a file, one per each device
* `cli_configure.py` - configures network devices based on Jinja2 template `templates/config.j2`
* `find_mac.py` - find a mac address location (attached to a switch or on any network device). It was built for a specific topology and needs to be slightly reworked to support an arbitrary topology.
* `netconf_save_config.py` - retrieves XML configuration via NETCONF and saves it to a file, one per each device
* `restconf_get_lldp_neighbors.py` - retrieves LLDP details using OpenConfig LLDP YANG model + RESTCONF as a tranport protocol. Prints all connections on the console
* `build_network_diagram_lldp.py` - retrieves LLDP details using OpenConfig LLDP YANG model + RESTCONF as a tranport protocol, then parses them,  builds a graph and creates a network diagram based on that graph
* `netconf_configure.py` - configures network devices using NETCONF where the data resides in YAML files. Jinja XML templates are NOT used.