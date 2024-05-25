from utils import get_ip, get_all_ip

def get_radiology_allowed_routes():
    return {
        #Switch 1
        1: {
            get_ip("d1"): { get_ip("d2"): 4, get_ip("cd_serv"): 4, get_ip("ent_serv"): 4, get_ip("rad_serv"): 4, get_ip("r1"): 4, get_ip("r2"): 4 },
            get_ip("d2"): { get_ip("d1"): 3, get_ip("cd_serv"): 3, get_ip("ent_serv"): 3, get_ip("rad_serv"): 3, get_ip("r1"): 3, get_ip("r2"): 3 },
            get_ip("cd_serv"): { get_ip("d1"): 5, get_ip("d2"): 5 },
            get_ip("rad_serv"): { get_ip("d1"): 1, get_ip("d2"): 1 },
            get_ip("r1"): { get_ip("d1"): 1, get_ip("d2"): 1 },
            get_ip("r2"): { get_ip("d1"): 1, get_ip("d2"): 1 },
            get_ip("ent_serv"): { get_ip("d1"): 2, get_ip("d2"): 2 }

        },

        #Switch 2
        2: {
            get_ip("d1"): { get_ip("rad_serv"): 2, get_ip("r1"): 2, get_ip("r2"): 2 },
            get_ip("d2"): { get_ip("rad_serv"): 2, get_ip("r1"): 2, get_ip("r2"): 2 },
            get_ip("rad_serv"): { get_ip("d1"): 1, get_ip("d2"): 1 },
            get_ip("cd_serv"): { get_ip("r1"): 2, get_ip("r2"): 2 },
            get_ip("r1"): { get_ip("cd_serv"): 1, get_ip("d1"): 1, get_ip("d2"): 1 },
            get_ip("r2"): { get_ip("cd_serv"): 1, get_ip("d1"): 1, get_ip("d2"): 1 },
        },

        #Switch 3
        3: {
            get_ip("r1"): { get_ip("d1"): 4, get_ip("d2"): 4, get_ip("rad_serv"): 4 },
            get_ip("r2"): { get_ip("d1"): 1, get_ip("d2"): 1, get_ip("rad_serv"): 1 },
            get_ip("rad_serv"): { get_ip("d1"): 3, get_ip("d2"): 3, get_ip("r1"): 3, get_ip("r2"): 3 },
            get_ip("d1"): { get_ip("rad_serv"): 2, get_ip("r1"): 2, get_ip("r2"): 2 },
            get_ip("d2"): { get_ip("rad_serv"): 2, get_ip("r1"): 2, get_ip("r2"): 2 }
        },

        #Switch 4
        4: { 
            get_ip("p1"): { get_ip("ent_serv"): 3 }, 
            get_ip("p2"): { get_ip("ent_serv"): 1 }, 
            get_ip("ent_serv"): { get_ip("d1"): 2, get_ip("d2"): 2, get_ip("p1"): 2, get_ip("p2"): 2},      
            get_ip("d1"): { get_ip("ent_serv"): 4 },
            get_ip("d2"): { get_ip("ent_serv"): 4 }
        }
    }

def get_radiology_forbidden_routes():

    return {
        get_ip("d1"): [ get_ip("p1"), get_ip("p2"), get_ip("back_serv") ],
        get_ip("d2"): [ get_ip("p1"), get_ip("p2"), get_ip("back_serv") ],

        get_ip("p1"): set(get_all_ip()).difference([ get_ip("ent_serv") ]),
        get_ip("p2"): set(get_all_ip()).difference([ get_ip("ent_serv") ]),

        get_ip("r1"): set(get_all_ip()).difference([ get_ip("d1"), get_ip("d2"), get_ip("rad_serv") ]),
        get_ip("r2"): set(get_all_ip()).difference([ get_ip("d1"), get_ip("d2"), get_ip("rad_serv") ]),

        get_ip("ent_serv"): set(get_all_ip()).difference([ get_ip("d1"), get_ip("d2"), get_ip("p1"), get_ip("p2") ]),
        get_ip("rad_serv"): set(get_all_ip()).difference([ get_ip("d1"), get_ip("d2"), get_ip("r1"), get_ip("r2") ]),
        get_ip("cd_serv"): set(get_all_ip()).difference([ get_ip("d1"), get_ip("d2"), get_ip("r1"), get_ip("r2") ]),
        get_ip("back_serv"): get_all_ip()
    }