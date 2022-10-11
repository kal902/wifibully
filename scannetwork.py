import os
import socket    
import multiprocessing
import subprocess
import time
import logging
#import arp_spoof
import getmac

class netscanner:

    def pinger(self, job_q, results_q):
        """
        Do Ping
        :param job_q:
        :param results_q:
        :return:
        """
        DEVNULL = open(os.devnull, 'w')
        while True:

            ip = job_q.get()

            if ip is None:
                break

            try:
                subprocess.check_call(['ping', '-c1', ip],
                                    stdout=DEVNULL)
                results_q.put(ip)
            except:
                pass


    def get_my_ip(self):
        """
        Find my IP address
        :return:
        """
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except OSError:
            logging.error('could not get my ip, not connected to network')
            return 'n/a'


    def map_network(self, pool_size=255):
        """
        Maps the network
        :param pool_size: amount of parallel ping processes
        :return: list of valid ip addresses
        """
        
        ip_list = []
        
        # get my IP and compose a base like 192.168.1.xxx
        my_ip = self.get_my_ip()
        print('my ip: ',my_ip)
        # stop further processing if my ip is null
        if my_ip == 'n/a':
            return None
        
        ip_parts = self.get_my_ip().split('.')

        base_ip = ip_parts[0] + '.' + ip_parts[1] + '.' + ip_parts[2] + '.'
        
        # prepare the jobs queue
        jobs = multiprocessing.Queue()
        results = multiprocessing.Queue()
        
        pool = [multiprocessing.Process(target=self.pinger, args=(jobs, results)) for i in range(pool_size)]
        logging.info('starting network mapper process')
        for p in pool:
            p.start()
        
        # cue hte ping processes
        for i in range(1, 255):
            jobs.put(base_ip + '{0}'.format(i))
        
        for p in pool:
            jobs.put(None)
        
        for p in pool:
            p.join()
        
        # collect the results
        while not results.empty():
            ip = results.get()
            mac = getmac.get_mac_address(ip=ip, network_request=True)

            ip_list.append((ip, mac))
        return ip_list
