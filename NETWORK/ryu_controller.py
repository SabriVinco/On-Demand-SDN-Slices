from collections import deque
from os import walk
import os

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
import time
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
        self.auto_enabled = False

        self.conn:socket = None

        # Thread per monitoraggio comandi dalla GUI
        self.thread = hub.spawn(self._monitor)
        self.auto_thread = None


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
                        "./QoS_and_Queue.sh",
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
            Add flow to the flow table of the selected switch
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
            f"ip,priority={priority},nw_src={ip_src},nw_dst={ip_dst},idle_timeout=0,actions=set_queue:{queue_n},output={port},pop_queue"
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

        assert scenario == str(Scenario.DEFAULT) or scenario == str(Scenario.RADIOLOGY) or scenario == str(Scenario.NIGHT)

        print('Enabling new scenario')

        self.current_scenario = int(scenario)

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

        if self.conn != None:
            print("Flows cleared")
           

        for dp_i in self.switch_datapaths_cache:
            switch_dp = self.switch_datapaths_cache[dp_i]

            self._flow_entry_empty(switch_dp)
        
        if self.conn != None:
            print("Initialized switches")

    
    def _monitor(self):
        '''
            Secondary thread that manages TCP connections from the GUI
        '''

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self.BIND_ADDRESS, self.BIND_PORT))
        print('\n\nWaiting for the GUI connection...')
        sock.listen(1)
        self.conn, addr = sock.accept()
        print(f"Connected: {self.conn} - {addr} ")

        while True:
            data = self.conn.recv(1024)
            if not data: 
                break
            
            msg_recv = data.decode("utf-8")
            if msg_recv == str(Scenario.DEFAULT) or msg_recv == str(Scenario.RADIOLOGY) or msg_recv == str(Scenario.NIGHT):

                if self.auto_enabled == True:
                    hub.kill(self.auto_thread)
                    self.send_message_to_GUI(f"\n*** AUTOMATIC MODE OFF ***" )
                    time.sleep(0.1)
                    self.auto_enabled = False

                if(msg_recv == str(Scenario.DEFAULT)):
                    req_scenario = "DEFAULT"
                elif(msg_recv == str(Scenario.RADIOLOGY)):
                    req_scenario = "RADIOLOGY"
                elif(msg_recv == str(Scenario.NIGHT)):
                    req_scenario = "NIGHT"
                self.send_message_to_GUI(f"Change scenario request received: {req_scenario}" )   
                self.init_flows_slice(msg_recv)
                self.send_message_to_GUI(f"{req_scenario} enabled" )

            if msg_recv == str(Scenario.AUTO):
                if self.auto_enabled == False:
                    self.auto_thread = hub.spawn(self.auto_mode)
                    self.auto_enabled = True
                else:
                    hub.kill(self.auto_thread)
                    self.send_message_to_GUI(f"\n*** AUTOMATIC MODE OFF ***" )
                    time.sleep(0.1)
                    self.init_flows_slice(str(Scenario.DEFAULT))             
                    self.send_message_to_GUI(f"\nDEFAULT enabled" )
                    self.auto_enabled = False

    def auto_mode(self):
        self.send_message_to_GUI(f"\n*** AUTOMATIC MODE ON ***" )
        while True:
            # Start DEFAULT
            self.init_flows_slice(str(Scenario.DEFAULT)) 
            time.sleep(0.1)
            self.send_message_to_GUI(f"DEFAULT enabled" )
            time.sleep(10)
            
            # Start RADIOLOGY
            self.init_flows_slice(str(Scenario.RADIOLOGY)) 
            time.sleep(0.1)
            self.send_message_to_GUI(f"RADIOLOGY enabled" )
            time.sleep(10)

            # Start NIGHT
            self.init_flows_slice(str(Scenario.NIGHT))
            time.sleep(0.1)
            self.send_message_to_GUI(f"NIGHT enabled" )
            time.sleep(10)
                
    def send_message_to_GUI(self, message):
        try:
            chunks = [message[i:i+1024] for i in range(0, len(message), 1024)]
            for chunk in chunks:
                self.conn.sendall(chunk.encode("UTF-8"))
        except Exception as e:
            print(f"Error in communication with GUI: {e}")

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        '''
            Called every time the controller receives a packet
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

        print(f"Packet-in information: [src={src_addr}, dst={dst_addr}]")

        if self.permitted[self.current_scenario] is None or self.prohibited[self.current_scenario] is None:
            print(f"Unknown route from {src_addr} to {dst_addr}")
            return

        port_mapping: Dict[int, Dict[str, int]] = self.permitted[self.current_scenario]
        prohibited: Dict[str, Set[str]] = self.prohibited[self.current_scenario]

        if src_addr in prohibited and dst_addr in prohibited[src_addr]:
            print(f"Communication forbidden from {src_addr} to {dst_addr}")
            return 

        if dpid in port_mapping:

            if dst_addr in port_mapping[dpid]:

                out_port: Dict | Tuple | int = port_mapping[dpid][dst_addr]

                if isinstance(out_port, Dict):
                    if src_addr in out_port:
                        out_port = out_port[src_addr]
                    else: 
                        print(f"Communication unspecified from {src_addr} to {dst_addr}")
                        return

                #Queue usage
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






