#!/usr/bin/bash

echo '---------------- Switch 1 ---------------- '
# Fast link to S4 - 2 queues
echo 'creating two queues on port 1...'
sudo ovs-vsctl set port s1-eth1 qos=@newqos -- \
--id=@newqos create QoS type=linux-htb \
other-config:max-rate=1000000000 \
queues:252=@1q \
queues:251=@2q -- \
--id=@1q create queue other-config:min-rate=200000000 other-config:max-rate=700000000 -- \
--id=@2q create queue other-config:min-rate=200000000 other-config:max-rate=300000000
echo ' ' 

# Slow link to S5
echo 'slow link to s5...'
sudo ovs-vsctl set port s1-eth2 qos=@newqos -- \
--id=@newqos create QoS type=linux-htb \
other-config:max-rate=20000000 \


# Host links to d1, r1
echo 'link to d1...'
sudo ovs-vsctl set port s1-eth3 qos=@newqos -- \
--id=@newqos create QoS type=linux-htb \
other-config:max-rate=1000000000 \
echo ' '


echo 'link to r1...'
sudo ovs-vsctl set port s1-eth4 qos=@newqos -- \
--id=@newqos create QoS type=linux-htb \
other-config:max-rate=1000000000 \


echo '---------------- Switch 2 ---------------- '
# Fast link to S4
echo 'fast link to s4...'
sudo ovs-vsctl set port s2-eth1 qos=@newqos -- \
--id=@newqos create QoS type=linux-htb \
other-config:max-rate=1000000000 \
echo ' '

# Host link to back_serv 
echo 'link to back_serv...'
sudo ovs-vsctl set port s2-eth2 qos=@newqos -- \
--id=@newqos create QoS type=linux-htb \
other-config:max-rate=1000000000 \


echo '---------------- Switch 3 ---------------- '
# Fast link to S4 - 2 queues
echo 'creating two queues on port 4...'
sudo ovs-vsctl set port s3-eth4 qos=@newqos -- \
--id=@newqos create QoS type=linux-htb \
other-config:max-rate=1000000000 \
queues:232=@1q \
queues:231=@2q -- \
--id=@1q create queue other-config:min-rate=200000000 other-config:max-rate=700000000 -- \
--id=@2q create queue other-config:min-rate=200000000 other-config:max-rate=300000000
echo ' '

# Slow link to S5
echo 'slow link to s5...'
sudo ovs-vsctl set port s3-eth3 qos=@newqos -- \
--id=@newqos create QoS type=linux-htb \
other-config:max-rate=20000000 \

# Host links to d2, r2
echo 'link to r2...'
sudo ovs-vsctl set port s3-eth1 qos=@newqos -- \
--id=@newqos create QoS type=linux-htb \
other-config:max-rate=1000000000 \

echo 'link to d2...'
sudo ovs-vsctl set port s3-eth2 qos=@newqos -- \
--id=@newqos create QoS type=linux-htb \
other-config:max-rate=1000000000 \


echo '---------------- Switch 4 ----------------'
# Fast link to S1 - 2 queues
echo 'creating two queues on port 1...'
sudo ovs-vsctl set port s4-eth1 qos=@newqos -- \
--id=@newqos create QoS type=linux-htb \
other-config:max-rate=1000000000 \
queues:522=@1q \
queues:521=@2q -- \
--id=@1q create queue other-config:min-rate=200000000 other-config:max-rate=700000000 -- \
--id=@2q create queue other-config:min-rate=200000000 other-config:max-rate=300000000
echo ' '

# Fast link to S2
echo 'fast link to s2...'
sudo ovs-vsctl set port s4-eth2 qos=@newqos -- \
--id=@newqos create QoS type=linux-htb \
other-config:max-rate=1000000000 \

# Fast link to S3 - 2 queues
echo 'creating two queues on port 3...'
sudo ovs-vsctl set port s4-eth3 qos=@newqos -- \
--id=@newqos create QoS type=linux-htb \
other-config:max-rate=1000000000 \
queues:322=@1q \
queues:321=@2q -- \
--id=@1q create queue other-config:min-rate=200000000 other-config:max-rate=700000000 -- \
--id=@2q create queue other-config:min-rate=200000000 other-config:max-rate=300000000
echo ' '

# Host link to ho_serv
echo 'link to ho_serv...'
sudo ovs-vsctl set port s4-eth4 qos=@newqos -- \
--id=@newqos create QoS type=linux-htb \
other-config:max-rate=1000000000 \

echo '---------------- Switch 5 ----------------'
# Slow links to S1, S3
echo 'slow link to s3...'
sudo ovs-vsctl set port s5-eth1 qos=@newqos -- \
--id=@newqos create QoS type=linux-htb \
other-config:max-rate=20000000 \

echo 'slow link to s1...'
sudo ovs-vsctl set port s5-eth5 qos=@newqos -- \
--id=@newqos create QoS type=linux-htb \
other-config:max-rate=20000000 \

# Host links to p1, p2, ent_serv
echo 'link to p2...'
sudo ovs-vsctl set port s5-eth2 qos=@newqos -- \
--id=@newqos create QoS type=linux-htb \
other-config:max-rate=1000000000 \

echo 'link to ent_serv...'
sudo ovs-vsctl set port s5-eth3 qos=@newqos -- \
--id=@newqos create QoS type=linux-htb \
other-config:max-rate=1000000000 \

echo 'link to p1...'
sudo ovs-vsctl set port s5-eth4 qos=@newqos -- \
--id=@newqos create QoS type=linux-htb \
other-config:max-rate=1000000000 \