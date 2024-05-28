#!/usr/bin/bash

# ---------------- Switch 1 ----------------
# Fast link to S4 - 2 queues
sudo ovs-vsctl -- \ 
set port s1-eth1 qos=@newqos -- \
--id=@newqos create QoS type=linux-htb \
other-config:max-rate=1000000000 \
queues:252=@1q \
queues:251=@2q -- \
--id=@1q create queue other-config:min-rate=200000000 other-config:max-rate=700000000 -- \
--id=@2q create queue other-config:min-rate=200000000 other-config:max-rate=300000000

# Slow link to S5
sudo ovs-vsctl -- \ 
set port s1-eth2 qos=@newqos -- \
--id=@newqos create QoS type=linux-htb \
other-config:max-rate=20000000 \

# Host links to d1, r1
sudo ovs-vsctl -- \ 
set port s1-eth3 qos=@newqos -- \
set port s1-eth4 qos=@newqos -- \
--id=@newqos create QoS type=linux-htb \
other-config:max-rate=1000000000 \

# ---------------- Switch 2 ----------------
# Fast link to S4
sudo ovs-vsctl -- \
set port s2-eth1 qos=@newqos -- \
--id=@newqos create QoS type=linux-htb \
other-config:max-rate=1000000000 \

# Host link to back_serv
sudo ovs-vsctl -- \ 
set port s2-eth2 qos=@newqos -- \
--id=@newqos create QoS type=linux-htb \
other-config:max-rate=1000000000 \

# ---------------- Switch 3 ----------------
# Fast link to S4 - 2 queues
sudo ovs-vsctl -- \ 
set port s1-eth4 qos=@newqos -- \
--id=@newqos create QoS type=linux-htb \
other-config:max-rate=1000000000 \
queues:232=@1q \
queues:231=@2q -- \
--id=@1q create queue other-config:min-rate=200000000 other-config:max-rate=700000000 -- \
--id=@2q create queue other-config:min-rate=200000000 other-config:max-rate=300000000

# Slow link to S5
sudo ovs-vsctl -- \ 
set port s1-eth3 qos=@newqos -- \
--id=@newqos create QoS type=linux-htb \
other-config:max-rate=20000000 \

# Host links to d2, r2
sudo ovs-vsctl -- \ 
set port s1-eth1 qos=@newqos -- \
set port s1-eth2 qos=@newqos -- \
--id=@newqos create QoS type=linux-htb \
other-config:max-rate=1000000000 \

# ---------------- Switch 4 ----------------
# Fast link to S1 - 2 queues
sudo ovs-vsctl -- \
set port s1-eth1 qos=@newqos -- \
--id=@newqos create QoS type=linux-htb \
other-config:max-rate=1000000000 \
queues:522=@1q \
queues:521=@2q -- \
--id=@1q create queue other-config:min-rate=200000000 other-config:max-rate=700000000 -- \
--id=@2q create queue other-config:min-rate=200000000 other-config:max-rate=300000000

# Fast link to S2
sudo ovs-vsctl -- \
set port s1-eth2 qos=@newqos -- \
--id=@newqos create QoS type=linux-htb \
other-config:max-rate=1000000000 \

# Fast link to S3 - 2 queues
sudo ovs-vsctl -- \
set port s1-eth3 qos=@newqos -- \
--id=@newqos create QoS type=linux-htb \
other-config:max-rate=1000000000 \
queues:322=@1q \
queues:321=@2q -- \
--id=@1q create queue other-config:min-rate=200000000 other-config:max-rate=700000000 -- \
--id=@2q create queue other-config:min-rate=200000000 other-config:max-rate=300000000

# Host link to ho_serv
sudo ovs-vsctl -- \
set port s4-eth4 qos=@newqos -- \
--id=@newqos create QoS type=linux-htb \
other-config:max-rate=1000000000 \

# ---------------- Switch 5 ----------------
# Slow links to S1, S3
sudo ovs-vsctl -- \ 
set port s1-eth1 qos=@newqos -- \
set port s1-eth5 qos=@newqos -- \
--id=@newqos create QoS type=linux-htb \
other-config:max-rate=20000000 \

# Host links to p1, p2, ent_serv
sudo ovs-vsctl -- \
set port s4-eth2 qos=@newqos -- \
set port s4-eth3 qos=@newqos -- \
set port s4-eth4 qos=@newqos -- \
--id=@newqos create QoS type=linux-htb \
other-config:max-rate=1000000000 \