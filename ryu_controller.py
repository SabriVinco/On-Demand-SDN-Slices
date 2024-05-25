from collections import deque
from os import walk

from ryu.ofproto import ofproto_v1_3
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, DEAD_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet, ipv4
from ryu.lib.packet import ether_types
from ryu.lib import hub
from mininet.log import info,debug, setLogLevel
import socket
import subprocess
from subprocess import PIPE, STDOUT, check_output
import logging

from typing import List, Optional, Dict, Set, Tuple

from scenarios.default import get_default_allowed_routes, get_default_forbidden_routes
from scenarios.radiology import get_radiology_allowed_routes, get_radiology_forbidden_routes
from scenarios.night import get_night_allowed_routes, get_night_forbidden_routes

from utils import Scenario, all_switches


class Slicing(app_manager.RyuApp):
    # Tested OFP version
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(Slicing, self).__init__(*args, **kwargs)        

        self.log_to_socket = deque()

        self.BIND_ADDRESS = "0.0.0.0"
        self.BIND_PORT = 8083

        self.permitted: List[Optional[Dict[int, Dict[str, int]]]] = [ None, None, None ] 
        self.prohibited: List[Optional[Dict[str, Set[str]]]] = [ None, None, None ] 

        self.permitted[Scenario.DEFAULT] = get_default_allowed_routes()
        self.prohibited[Scenario.DEFAULT] = get_default_forbidden_routes()

        self.permitted[Scenario.RADIOLOGY] = get_radiology_allowed_routes()
        self.prohibited[Scenario.RADIOLOGY] = get_radiology_forbidden_routes()

        self.permitted[Scenario.NIGHT] = get_night_allowed_routes()
        self.prohibited[Scenario.NIGHT] = get_night_forbidden_routes()
        
        self.switch_datapaths_cache = {}

        self.current_scenario = Scenario.DEFAULT

        # Thread per monitoraggio comandi dalla GUI
        self.thread = hub.spawn(self._monitor)

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER) 
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath

        self._flow_entry_empty(datapath)

    def _flow_entry_empty(self, datapath):
        # Install the table-miss flow entry.
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        match = parser.OFPMatch()
        # Il pacchetto viene inviato direttamente al controller, senza rimanere nel buffer dello switch
        actions = [
            parser.OFPActionOutput(ofproto.OFPP_CONTROLLER, ofproto.OFPCML_NO_BUFFER)
        ]
        self.add_flow(datapath, 0, match, actions)

    @set_ev_cls(ofp_event.EventOFPStateChange, [MAIN_DISPATCHER, DEAD_DISPATCHER])
    def _state_change_handler(self, ev):
        datapath = ev.datapath
        if ev.state == MAIN_DISPATCHER:
            if datapath.id not in self.switch_datapaths_cache:
                self.switch_datapaths_cache[datapath.id] = datapath

                if len(self.switch_datapaths_cache) == len(all_switches()):

                    command = [
                        "./QoS and Queues/QoS.sh",
                    ]

                    completed = subprocess.run(command, stdout=PIPE, stderr=STDOUT)

                    if completed.returncode == 0:
                        pass
                    else:
                        info(completed.stdout)


        elif ev.state == DEAD_DISPATCHER:
            if datapath.id in self.switch_datapaths_cache:
                del self.switch_datapaths_cache[datapath.id]

    def add_flow(self, datapath, priority, match, actions):
        '''
            Add flow to the flow table of the selected switch ( by its
            datapath )
        '''
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        mod = parser.OFPFlowMod(
            datapath=datapath, priority=priority, match=match, instructions=inst
        )
        datapath.send_msg(mod)

    def _send_package(self, msg, datapath: app_manager.Datapath, in_port, actions):
        '''
            Sends a package directly using the controller, before the actual flow 
            table entry is used, so that the first ping 
        '''
        data = None
        ofproto = datapath.ofproto
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        out = datapath.ofproto_parser.OFPPacketOut(
            datapath=datapath,
            buffer_id=msg.buffer_id,
            in_port=in_port,
            actions=actions,
            data=data,
        )
        datapath.send_msg(out)

    def _create_flow_queue(self, dpid: int, ip_src: str, ip_dst: str, queue_n: int, priority: int, port: int):
        '''
            To create flow table entry wrapping ovs-ofctl. Workaround to the
            ryu not fully-working queue implementation
        '''
        command = [
            "ovs-ofctl",
            "add-flow",
            f"s{dpid}",
            f"ip,priority={priority},nw_src={ip_src},nw_dst={ip_dst},idle_timeout=0,output={port},normal"
        ]

        completed = subprocess.run(command, stdout=PIPE, stderr=STDOUT)

        if completed.returncode == 0:
            pass
        else:
            info(completed.stdout)


    def init_flows_slice( self, scenario ):
        '''
            Method to re-initialize the switches to apply the slicing mode.
            Flow tables are cleared and the default route is configured
        '''

        # Se falso viene sollevata un'eccezione
        assert scenario == str(Scenario.DEFAULT) or scenario == str(Scenario.RADIOLOGY) or scenario == str(Scenario.NIGHT) 

        self.current_scenario = int(scenario)

        # DEBUG: print the value of the scenario

        # Per ogni datapath presente nella cache
        for dp_i in self.switch_datapaths_cache:

            switch_dp = self.switch_datapaths_cache[dp_i]

            ofp_parser = switch_dp.ofproto_parser
            ofp = switch_dp.ofproto

            # Messaggio per la cancellazione delle tabelle
            mod = ofp_parser.OFPFlowMod(
                datapath=switch_dp,
                table_id=ofp.OFPTT_ALL,
                command=ofp.OFPFC_DELETE,
                out_port=ofp.OFPP_ANY,
                out_group=ofp.OFPG_ANY
            )

            switch_dp.send_msg(mod)

        for dp_i in self.switch_datapaths_cache:
            switch_dp = self.switch_datapaths_cache[dp_i]

            self._flow_entry_empty(switch_dp)

    
    def _monitor(self):
        '''
            Secondary thread that manages TCP connections from the GUI
        '''

        # DEBUG: thread starts
        print("Partito il thread per il monitoraggio dei segnali")

        # Creazione socket e attivazione per l'ascolto
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self.BIND_ADDRESS, self.BIND_PORT))
        sock.listen()

        print('Controller in attesa di comandi...')

        while True:
            conn, addr = sock.accept()

            # DEBUG: arrivata connessione
            print("Arrivata connessione")

            while True:
                data = conn.recv(1024)
                if not data: 
                    break
                
                msg_recv = data.decode("utf-8")
                if msg_recv == str(Scenario.DEFAULT) or msg_recv == str(Scenario.RADIOLOGY) or msg_recv == str(Scenario.NIGHT):
                    self.init_flows_slice(msg_recv)
                    #DEBUG: Attivato scenario richiesto
                




    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        '''
            Main packet handling function. It works by using the predefined
            topology, based on the actual scenario. 
        '''
        msg = ev.msg

        datapath: app_manager.Datapath = msg.datapath
        dpid = datapath.id

        ofproto = datapath.ofproto
        in_port = msg.match["in_port"]

        pkt = packet.Packet(msg.data)
        eth: Optional[ethernet.ethernet] = pkt.get_protocol(ethernet.ethernet) 
        lv3_pkg: Optional[ipv4.ipv4] = pkt.get_protocol(ipv4.ipv4) 

        if (
            eth is None or
            lv3_pkg is None or
            dpid is None or
            eth.ethertype == ether_types.ETH_TYPE_LLDP
        ):
            return

        dst_addr = lv3_pkg.dst
        src_addr = lv3_pkg.src 

        if self.permitted[self.current_scenario] is None or self.prohibited[self.current_scenario] is None:
            return

        port_mapping: Dict[int, Dict[str, int]] = self.permitted[self.current_scenario]
        prohibited: Dict[str, Set[str]] = self.prohibited[self.current_scenario]

        if src_addr in prohibited and dst_addr in prohibited[src_addr]:
            return 

        if dpid in port_mapping:

            if dst_addr in port_mapping[dpid]:

                out_port: Dict | Tuple | int = port_mapping[dpid][dst_addr]

                if isinstance(out_port, Dict):
                    if src_addr in out_port:
                        out_port = out_port[src_addr]
                    else: 
                        return

                if isinstance(out_port, Tuple):
                    out_port, queue_id = out_port

                    self._create_flow_queue(
                        dpid=dpid,
                        ip_src=src_addr, 
                        ip_dst=dst_addr,
                        queue_n=queue_id,
                        priority=2,
                        port=out_port
                    )

                    actions = [ datapath.ofproto_parser.OFPActionOutput(out_port) ]
                    self._send_package(msg, datapath, in_port, actions)

                else:
                    actions = [datapath.ofproto_parser.OFPActionOutput(out_port)]

                    match = datapath.ofproto_parser.OFPMatch(eth_type=0x800, ipv4_src=src_addr, ipv4_dst=dst_addr)

                    self.add_flow(datapath, 2, match, actions)
                    self._send_package(msg, datapath, in_port, actions)





