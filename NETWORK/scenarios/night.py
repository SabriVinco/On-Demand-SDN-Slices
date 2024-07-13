from utils import get_ip, get_all_ip


def get_night_allowed_routes():
    return {
        #Switch 1
        1: { },

        #Switch 2
        2: {
            get_ip("back_serv"): { get_ip("ho_serv"): 2 },
            get_ip("ho_serv"): { get_ip("back_serv"): 1 }
        },

        #Switch 3
        3: { },

        #Switch 4
        4: { 
            get_ip("back_serv"): { get_ip("ho_serv"): 2 },
            get_ip("ho_serv"): { get_ip("back_serv"): 4 }
        },

        #Switch 5
        5: { }
    }



def get_night_forbidden_routes():

    return {
        get_ip("d1"): get_all_ip(),
        get_ip("d2"): get_all_ip(),

        get_ip("p1"): get_all_ip(),
        get_ip("p2"): get_all_ip(),

        get_ip("r1"): get_all_ip(),
        get_ip("r2"): get_all_ip(),

        get_ip("ent_serv"): get_all_ip(),
        get_ip("ho_serv"): set(get_all_ip()).difference([ get_ip("back_serv") ]),
        get_ip("back_serv"): set(get_all_ip()).difference([ get_ip("ho_serv") ])
    }