
# SDN Broadcast Traffic Control System

## Problem Statement
Traditional networks suffer from broadcast storms. This project implements an SDN controller to detect, log, and selectively forward broadcast traffic to reduce network overhead.

## Setup
1. **Prerequisites:** Ubuntu 24.04, Mininet, Ryu.
2. **Environment:** Python 3.12 Virtual Environment.
3. **Execution:**
   - Run Controller: `python3 ryu/bin/ryu-manager broadcast_ctrl.py`
   - Run Topology: `sudo mn --custom my_topo.py --topo myproject --controller remote`

## Evaluation & Results
- **Detection:** Controller successfully identifies ARP broadcast packets.
- **Flooding Control:** Selective forwarding rules are pushed to the switch after the first discovery.
- **Performance:** Reduced Packet_In events for subsequent broadcasts from the same host.

## Proof of Execution
![Ping Results](./screenshots/ping_result.png)
![Flow Tables](./screenshots/flow_table.png)
