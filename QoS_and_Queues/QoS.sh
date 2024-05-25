#!/usr/bin/bash

# ---------------- Switch 1 ----------------
# Fast link to S2
sudo ovs-vsctl -- \ 
set port s1-eth1 qos=@newqos -- \
--id=@newqos create QoS type=linux-htb \
other-config:max-rate=5000000000 \

# Slow link to S4
sudo ovs-vsctl -- \ 
set port s1-eth2 qos=@newqos -- \
--id=@newqos create QoS type=linux-htb \
other-config:max-rate=20000000 \

# Host links to d1, d2, cd_serv
sudo ovs-vsctl -- \ 
set port s1-eth3 qos=@newqos -- \
set port s1-eth4 qos=@newqos -- \
set port s1-eth5 qos=@newqos -- \
--id=@newqos create QoS type=linux-htb \
other-config:max-rate=10000000 \

# ---------------- Switch 2 ----------------
# Fast links to S3, S1
sudo ovs-vsctl -- \
set port s2-eth1 qos=@newqos -- \
set port s2-eth2 qos=@newqos
--id=@newqos create QoS type=linux-htb \
other-config:max-rate=100000000 \

# Host link to back_serv
sudo ovs-vsctl -- \ 
set port s2-eth3 qos=@newqos -- \
--id=@newqos create QoS type=linux-htb \
other-config:max-rate=5000000000 \

# ---------------- Switch 3 ----------------

# Host link to r2, rad_serv, r1
sudo ovs-vsctl -- \
set port s3-eth1 qos=@newqos -- \
set port s3-eth3 qos=@newqos -- \
set port s3-eth4 qos=@newqos -- \
--id=@newqos create QoS type=linux-htb \
other-config:max-rate=10000000 \

# Fast link to S2
sudo ovs-vsctl -- \
set port s3-eth2 qos=@newqos -- \
--id=@newqos create QoS type=linux-htb \
other-config:max-rate=5000000000 \

# ---------------- Switch 4 ----------------
# Host link to p2, ent_serv, p1
sudo ovs-vsctl -- \
set port s4-eth1 qos=@newqos -- \
set port s4-eth2 qos=@newqos -- \
set port s4-eth3 qos=@newqos -- \
--id=@newqos create QoS type=linux-htb \
other-config:max-rate=10000000 \

# Slow link to S1
sudo ovs-vsctl -- \
set port s4-eth4 qos=@newqos -- \
--id=@newqos create QoS type=linux-htb \
other-config:max-rate=20000000 \

