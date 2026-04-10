from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet

class BroadcastTrafficControl(app_manager.RyuApp):
    # Using OpenFlow 1.3 as per industry standards
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(BroadcastTrafficControl, self).__init__(*args, **kwargs)

    # 1. HANDSHAKE: Set up the Table-Miss entry
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # Default rule: Send everything to the controller if no match found
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)

    # Helper function to install flows into the switch
    def add_flow(self, datapath, priority, match, actions):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                match=match, instructions=inst)
        datapath.send_msg(mod)

    # 2. PACKET-IN: Logic to detect and control broadcast traffic
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]

        dst = eth.dst
        src = eth.src

        # EXPECTATION: Detect broadcast packets (MAC: ff:ff:ff:ff:ff:ff)
        if dst == 'ff:ff:ff:ff:ff:ff':
            self.logger.info("--- BROADCAST DETECTED FROM %s ---", src)
            
            # EXPECTATION: Limit flooding & Selective Forwarding
            # We install a flow rule for this specific source so the switch
            # handles future broadcasts from this host without asking the controller.
            match = parser.OFPMatch(eth_src=src, eth_dst=dst)
            actions = [parser.OFPActionOutput(ofproto.OFPP_FLOOD)]
            
            # Priority 10 is higher than Table-Miss (0)
            self.add_flow(datapath, 10, match, actions)
            self.logger.info("ACTION: Selective Forwarding Rule Installed for %s", src)

        # Execute the action for the current packet
        actions = [parser.OFPActionOutput(ofproto.OFPP_FLOOD)]
        out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                  in_port=in_port, actions=actions, data=msg.data)
        datapath.send_msg(out)
