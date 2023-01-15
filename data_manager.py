import os
import pickle
import uuid
import logging

import settings
from scannetwork import netscanner

class datamanager:
    
    def __init__(self):
        self.scannet = netscanner()

        self.data_files_dir = "data"
        self.setting_data_file = os.path.join(self.data_files_dir,"setting.dat")
        self.devices_data_file = os.path.join(self.data_files_dir,"devices.dat")
        
        
        # check for data files
        if not os.path.exists(self.data_files_dir):
            os.mkdir(self.data_files_dir)

        if not os.path.exists(self.setting_data_file):
            self.init_settings()

        if not os.path.exists(self.devices_data_file):
            self.init_devices_data()
        
        # refresh settings (my_ip)
        setting = self.get_settings()
        setting.my_ip = self.scannet.get_my_ip()
        setting.my_mac = self.get_my_mac()
        
        self.save_settings(setting)
            
    
    def init_settings(self):
        # init setting data file with default settings
        logging.info('initializing setting')
        
        setting = self.default_setting()
        
        settingfile = open(self.setting_data_file, 'wb')
        pickle.dump(setting, settingfile)
        settingfile.close()
        
        logging.info('setting initialization finished')

    def init_devices_data(self):
        # init devices data file with empty python dict
        devicesfile = open(self.devices_data_file, 'wb')
        devices = {}
        pickle.dump(devices, devicesfile)
        devicesfile.close()

    def get_settings(self):
        try:
            with open(self.setting_data_file, 'rb') as f:
                setting = pickle.load(f)
                return setting
        except:
            logging.error('error while trying to read setting file')
            self.init_settings()

    def save_settings(self, setting):
        with open(self.setting_data_file, 'wb') as f:
            pickle.dump(setting, f)

    def get_devices(self):
        try:
            with open(self.devices_data_file, 'rb') as f:
                devices = pickle.load(f)
                return devices
        except:
            logging.error('error while trying to read devices file')
            self.init_devices_data()

    # not optimal method, as the method will access a file on each call       
    def get_device(self, device):
        devices = self.get_devices()
        try:
            device = devices[device]
            return device
        except KeyError:
            return None

    def add_device(self, mac, dev_name):
        devices = self.get_devices()

        devices[mac] = dev_name
        with open(self.devices_data_file, 'wb') as f:
            pickle.dump(devices, f)
        
    def default_setting(self):
        setting = settings.settings()
        
        setting.my_ip = self.scannet.get_my_ip()
        setting.poision_gateway = False
        setting.gateway_ip = "192.168.1.1"
        setting.gateway_mac = 'n/a'
        setting.this_pc_mac = self.get_my_mac()
        setting.time_interval = 5
        setting.hwsrc = 'n/a' # "hwsrc" value for the 'is-at' arp pkt

        return setting
    
    def get_my_mac(self):
    	return ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff)for ele in range(0,8*6,8)][::-1])


        