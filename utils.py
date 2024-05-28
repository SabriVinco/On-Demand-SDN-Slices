class Scenario():
    DEFAULT = 0
    RADIOLOGY = 1
    NIGHT = 2

def get_ip( hostname: str ):

    hostname_map = {
        "d1": "10.0.0.1",
        "d2": "10.0.0.2",

        "p1": "10.0.0.3",
        "p2": "10.0.0.4",

        "r1": "10.0.0.5",
        "r2": "10.0.0.6",

        "ent_serv": "10.0.0.7",
        "ho_serv": "10.0.0.8",
        "back_serv": "10.0.0.9",
    }

    return hostname_map[hostname]


def get_all_ip():
    return [
        get_ip("d1"),
        get_ip("d2"),
        get_ip("p1"),
        get_ip("p2"),
        get_ip("r1"),
        get_ip("r2"),
        get_ip("ent_serv"),
        get_ip("ho_serv"),
        get_ip("back_serv")
    ]

def all_switches():
    return [ "s1", "s2", "s3", "s4", "s5" ]

