from utils import get_ip, get_all_ip


def get_night_allowed_routes():
    return {
        #Switch 1
        1: {
            get_ip("cd_serv"): { get_ip("back_serv"): 5 },
            get_ip("back_serv"): { get_ip("cd_serv"): 1 }
        },

        #Switch 2
        2: {
            get_ip("back_serv"): { get_ip("cd_serv"): 3, get_ip("rad_serv"): 3 },
            get_ip("cd_serv"): { get_ip("back_serv"): 2 },
            get_ip("rad_serv"): { get_ip("back_serv"): 1 }
        },

        #Switch 3
        3: {
            get_ip("rad_serv"): { get_ip("back_serv"): 3 },
            get_ip("back_serv"): { get_ip("rad_serv"): 2 }
        },

        #Switch 4
        4: {  }
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
        get_ip("rad_serv"): set(get_all_ip()).difference([ get_ip("back_serv") ]),
        get_ip("cd_serv"): set(get_all_ip()).difference([ get_ip("back_serv") ]),
        get_ip("back_serv"): set(get_all_ip()).difference([ get_ip("cd_serv"), get_ip("rad_serv") ])
    }