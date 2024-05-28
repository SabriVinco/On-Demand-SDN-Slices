from comnetsemu.cli import CLI
from comnetsemu.net import Containernet, VNFManager
from comnetsemu.node import DockerHost 
from mininet.link import TCLink
from mininet.log import info, setLogLevel

from mininet.topo import Topo
from mininet.node import OVSKernelSwitch, RemoteController
    
class NetworkTopology(Topo):
    
    def __init__(self):

        Topo.__init__(self)

        giga_link = {}
        mega_link = {}
        host_link = {}
        
        #Doctors
        d1 = self.addHost(
            "d1",
            cls=DockerHost,
            dimage="dev_test",
            ip="10.0.0.1/24",
            mac="00:00:00:00:00:01",
            docker_args={"hostname": "d1"}
        )
        d2 = self.addHost(
            "d2",
            cls=DockerHost,
            dimage="dev_test",
            ip="10.0.0.2/24",
            mac="00:00:00:00:00:02",
            docker_args={"hostname": "d2"}
        )

        #Patients
        p1 = self.addHost(
            "p1",
            cls=DockerHost,
            dimage="dev_test",
            ip="10.0.0.3/24",
            mac="00:00:00:00:00:03",
            docker_args={"hostname": "p1"}
        )
        p2 = self.addHost(
            "p2",
            cls=DockerHost,
            dimage="dev_test",
            ip="10.0.0.4/24",
            mac="00:00:00:00:00:04",
            docker_args={"hostname": "p2"}
        )

        # Radiology Machines
        r1 = self.addHost(
            "r1",
            cls=DockerHost,
            dimage="dev_test",
            ip="10.0.0.5/24",
            mac="00:00:00:00:00:05",
            docker_args={"hostname": "r1"}
        )
        r2 = self.addHost(
            "r2",
            cls=DockerHost,
            dimage="dev_test",
            ip="10.0.0.6/24",
            mac="00:00:00:00:00:06",
            docker_args={"hostname": "r2"}
        )

        # Servers
        ent_serv = self.addHost(
            "ent_serv",
            cls=DockerHost,
            dimage="dev_test",
            ip="10.0.0.7/24",
            mac="00:00:00:00:01:01",
            docker_args={"hostname": "ent_serv"}
        )
        ho_serv = self.addHost(
            "ho_serv",
            cls=DockerHost,
            dimage="dev_test",
            ip="10.0.0.8/24",
            mac="00:00:00:00:01:02",
            docker_args={"hostname": "ho_serv"}
        )
        back_serv = self.addHost(
            "back_serv",
            cls=DockerHost,
            dimage="dev_test",
            ip="10.0.0.9/24",
            mac="00:00:00:00:01:03",
            docker_args={"hostname": "back_serv"}
        )
        
        for i in range(5):
            sconfig = {"dpid": "%016x" % (i + 1)}
            self.addSwitch("s%d" % (i + 1), **sconfig)

        #Switch links
        self.addLink("s1", "s4", 1, 1, **giga_link)
        self.addLink("s4", "s3", 3, 4, **giga_link)
        self.addLink("s4", "s2", 2, 1, **giga_link)
        self.addLink("s3", "s5", 3, 1, **mega_link)
        self.addLink("s1", "s5", 2, 5, **mega_link)
       
        #Doctor links
        self.addLink("d1", "s1", 1, 3, **host_link)
        self.addLink("d2", "s3", 1, 2, **host_link)

        #Patient links
        self.addLink("p1", "s5", 1, 4, **host_link)
        self.addLink("p2", "s5", 1, 2, **host_link)

        #Radiology links
        self.addLink("r1", "s1", 1, 4, **host_link)
        self.addLink("r2", "s3", 1, 1, **host_link)

        #Server links
        self.addLink("back_serv", "s2", 1, 2, **giga_link)
        self.addLink("ho_serv", "s4", 1, 4, **giga_link)
        self.addLink("ent_serv", "s5", 1, 3, **giga_link)

try:
    if __name__ == "__main__":
        
        setLogLevel("info")

        topo = NetworkTopology()
        net = Containernet(
            topo=topo,
            switch=OVSKernelSwitch,
            build=False,
            autoSetMacs=True,
            autoStaticArp=True,
            link=TCLink
        )

        mgr = VNFManager(net)

        info("*** Connecting to the controller\n")
        controller = RemoteController("c1", ip="127.0.0.1", port=6633)
        net.addController(controller)

        info("\n*** Starting network\n")
        
        net.build()
        net.start()
        
        k=CLI(net)

        net.stop()

except Exception as e: 
    print(e)
