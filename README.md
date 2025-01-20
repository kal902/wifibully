WiFi Bully
WiFi Bully is a Linux desktop application developed in Python, utilizing the Scapy library. Its primary purpose is to control internet access for clients connected to wireless or wired access points without disconnecting them from the network.

Key Features:
Internet Access Limitation:
WiFi Bully leverages ARP spoofing to restrict internet access for selected clients. By spoofing the clients' ARP cache, it alters the registered MAC address of the access point to a fake/decoy MAC address. This causes the clients' network requests to fail to reach the legitimate access point and instead get routed to the fake access point.

Man-in-the-Middle (MITM) Capabilities:
The program enables interception of a target's network traffic by routing it to a desired machine on the same network.

User-Friendly Interface:
WiFi Bully provides an easy-to-use graphical user interface (GUI) for efficient control and operation.

This tool is particularly useful for network security testing and traffic manipulation while maintaining connectivity for targeted clients.








