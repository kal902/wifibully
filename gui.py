import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from tkinter import simpledialog

from arp_spoof import arpspoof
from settings import settings
from scannetwork import netscanner

import time
import logging

class gui:

    def __init__(self, data_mgr):
        self.root = tk.Tk()
        self.root.title('wifibully')
    
        self.selection = {} # scanned wifi clients list
        self.poisiongateway = tk.IntVar() # checkbox variable
        self.gatewayip = tk.StringVar()
        self.hwsrc = tk.StringVar() # arp header value. pkts from clients will route to this mac
        self.timeinterval = tk.IntVar()

        # get saved settings from data_manager
        self.data_mgr = data_mgr
        self.savedsettings = self.data_mgr.get_settings()

        self.timeinterval.set(self.savedsettings.time_interval)


    def save_device(self):
        # get selected device name
        for index in self.selection:
            check = self.selection[index]
            if check.get() == 1:
                selected_dev = self.devices[index]
                dev_mac = selected_dev[1]
                dev_name = simpledialog.askstring("Input", f"enter device name for {dev_mac}",parent=self.root) #show dialog
                if dev_name == '' or dev_name == None:
                    return

                self.data_mgr.add_device(dev_mac, dev_name)
                logging.info('device saved')
                self.status_label.configure(text='device saved')
                return

    # start arp poisioning on selected devices
    def start_poision(self):
        for index in self.selection:
            # is checkbox/device selected
            check = self.selection[index]
            if check.get() == 1:
                selected_device = self.devices[index] # returns tuple (ip, mac)
                ip = selected_device[0]
                mac = selected_device[1]

                # start arp poisioning thread for this device
                arp = arpspoof(self.savedsettings, ip, mac)
                arp.start()
                logging.info(f'arp poision started on {ip}')
        

    def save_settings(self):
        poisiongateway = self.poisiongateway.get()
        gatewayip = self.gatewayip.get()
        hwsrc = self.hwsrc.get()
        timeinterval = self.timeinterval.get()

        newsetting = self.savedsettings # get copy of recent setting and modify new ones.
        if poisiongateway != self.savedsettings.poision_gateway:
            newsetting.poision_gateway = poisiongateway
            logging.info('poision gateway changed')
        if gatewayip != '' and gatewayip != self.savedsettings.gateway_ip:
            newsetting.gateway_ip = gatewayip
            logging.info('gateway ip changed')
        if hwsrc != '' and hwsrc != self.savedsettings.hwsrc:
            newsetting.hwsrc = hwsrc
            logging.info('hwsrc changed')
        if timeinterval != self.savedsettings.time_interval:
            newsetting.time_interval = timeinterval
            logging.info('time interval changed')

        # save setting
        self.data_mgr.save_settings(newsetting)
        self.savedsettings = newsetting
        logging.info('setting saved')
        self.status_label.configure(text='setting saved')
        self.reload_setting_ui() # reconstruct information fields with new data

    def scan(self):
        self.btn_scan.configure(state='disabled') # disable scan button
        self.status_label.configure(text='scanning network')

        scanner = netscanner()
        devices = scanner.map_network() # wifi clients

        if devices == None:
            print('map_network returned None. check your network connection.')
            self.btn_scan.configure(state='enabled')
            self.status_label.configure(text='scanning finished')
            return

        # remove gatewayip and myip from the list
        for device in devices: # device is tuple (ip, mac)
            if device[0] == self.savedsettings.my_ip:
                devices.remove(device)
            if device[0] == self.savedsettings.gateway_ip:
                devices.remove(device)

        self.devices = devices

        saved_devices = self.data_mgr.get_devices()

        # construct list of wifi clients with checkbox in the scrolledText
        iter = 0
        for ip, mac in self.devices:
            # a frame for each row, holding the three fields (ip, mac, devicename) and the checkbox
            row_frame = ttk.Frame(self.scroll)
            row_frame.grid(column=0, row=iter)

            # create int var for the checkbox with unique key which is the loop index
            self.selection[iter] = tk.IntVar()

            check = tk.Checkbutton(row_frame, variable=self.selection[iter])
            check.grid(column=0, row=0, padx=5)

            ip_lbl = tk.Label(row_frame, text=ip)
            ip_lbl.grid(column=1, row=0)

            mac_lbl = tk.Label(row_frame, text=mac)
            mac_lbl.grid(column=2, row=0, padx=5)
            
            # get device name if available/saved
            device_name = 'n/a'
            try:
                device_name = saved_devices[mac]
            except KeyError: # there is no value assossiated with this mac/key
                logging.warning('no devicename found for '+device_name)

            dev_name_lbl = tk.Label(row_frame, text=device_name)
            dev_name_lbl.grid(column=3, row=0, padx=5)

            self.scroll.window_create('end', window=row_frame)
            self.scroll.insert('end', '\n')

            iter += 1
        
        self.btn_scan.configure(state='enabled')
        self.status_label.configure(text='scanning finished')

    def build_gui(self):
        logging.info('building gui')
        ### left frame 
        ctrl_frame = ttk.LabelFrame(self.root, text='clients')
        ctrl_frame.grid(column=0, row=0, padx=5, pady=5)

        scrolw = 43
        scrolh = 20
        self.scroll = scrolledtext.ScrolledText(ctrl_frame, width=scrolw, height=scrolh, wrap=tk.WORD)
        self.scroll.grid(column=0, columnspan=3)

        ctrl_btn_frame = ttk.Frame(ctrl_frame)
        ctrl_btn_frame.grid(column=4, row=0, padx=5, sticky='N')

        self.btn_scan = ttk.Button(ctrl_btn_frame, text='scan', command=self.scan)
        self.btn_scan.grid(column=0,row=0, pady=5)

        self.btn_save = ttk.Button(ctrl_btn_frame, text='save', command=self.save_device)
        self.btn_save.grid(column=0,row=1, pady=5)

        self.btn_start = ttk.Button(ctrl_btn_frame, text='start', command=self.start_poision)
        self.btn_start.grid(column=0,row=2, pady=5, sticky=tk.S)

        self.status_label = tk.Label(ctrl_btn_frame)
        self.status_label.grid(column=0,row=3, pady=10)
        ### setting frame (right frame) ###

        main_right_frame = ttk.Frame(self.root)
        main_right_frame.grid(column=1, row=0, sticky='N')

        adv_frame = ttk.LabelFrame(main_right_frame, text='Advanced Setting')
        adv_frame.grid(column=0, row=0, padx=5, pady=5, sticky='N')

        left_frame = ttk.Frame(adv_frame)
        left_frame.grid(column=0, row=0)

        right_frame = ttk.Frame(adv_frame)
        right_frame.grid(column=1, row=0)

        # poision gateway ?
        tk.Label(left_frame, text='poision gateway: ').grid(column=0, row=0, sticky='E', pady=5, padx=5)

        poision_gateway = tk.Checkbutton(right_frame, variable=self.poisiongateway)
        poision_gateway.grid(column=1, row=0, pady=5, padx=5, sticky='W')

        # gateway ip 
        tk.Label(left_frame, text='gateway ip: ').grid(column=0, row=1, sticky="E", pady=5, padx=5)

        gateway_ip = ttk.Entry(right_frame, width=12, textvariable=self.gatewayip)
        gateway_ip.grid(column=1, row=1, pady=5, padx=5, sticky='W')

        # hwsrc
        tk.Label(left_frame, text='hwsrc mac: ').grid(column=0, row=2, sticky='E', pady=5, padx=5)

        hwsrc_entry = ttk.Entry(right_frame, width=12, textvariable=self.hwsrc)
        hwsrc_entry.grid(column=1, row=2, sticky='W', pady=5, padx=5,)

        # time interval to send arp spoof packets
        tk.Label(left_frame, text='time interval: ').grid(column=0, row=3, sticky='E', pady=5, padx=5)

        time_interval = ttk.Entry(right_frame, width=5, textvariable=self.timeinterval)
        time_interval.grid(column=1, row=3, sticky='W', pady=5, padx=5)
        
        # save setting btn
        tk.Label(left_frame, text=' ').grid(column=0, row=4, sticky='E', pady=5, padx=5,) # just for spacing

        save_setting_btn = ttk.Button(right_frame, text='save', command=self.save_settings)
        save_setting_btn.grid(column=1, row=4, sticky='W', padx=5, pady=5)

        #### status/saved setting information #####

        # frame holding current status and saved settings information
        info_frame = ttk.LabelFrame(main_right_frame, text='status info')
        info_frame.grid(column=0, row=1, padx=5, pady=5, sticky='S')

        left_frame_info = ttk.Frame(info_frame)
        left_frame_info.grid(column=0, row=0)

        right_frame_info = ttk.Frame(info_frame)
        right_frame_info.grid(column=1, row=0)

        # my ip info
        tk.Label(left_frame_info, text='my ip: ').grid(column=0, row=0, sticky='E')

        self.my_ip_info = tk.Label(right_frame_info, text=self.savedsettings.my_ip)
        self.my_ip_info.grid(column=1, row=0, sticky='W')

        # my mac info
        tk.Label(left_frame_info, text='my mac: ').grid(column=0, row=1, sticky='E')

        self.my_mac_info = tk.Label(right_frame_info, text=self.savedsettings.this_pc_mac)
        self.my_mac_info.grid(column=1, row=1, sticky='W')

        # gateway ip info
        tk.Label(left_frame_info, text='gateway ip: ').grid(column=0, row=2, sticky='E')

        self.gateway_ip_info = ttk.Label(right_frame_info, text=self.savedsettings.gateway_ip)
        self.gateway_ip_info.grid(column=1, row=2, sticky='W')

        # gateway mac info
        tk.Label(left_frame_info, text='gateway mac: ').grid(column=0, row=3, sticky='E')

        self.gateway_mac_info = tk.Label(right_frame_info, text=self.savedsettings.gateway_mac)
        self.gateway_mac_info.grid(column=1, row=3, sticky='W')
        
        # poision gateway
        tk.Label(left_frame_info, text='poision gateway: ').grid(column=0, row=4, sticky='E')

        poisiongateway = 'False'
        if self.savedsettings.poision_gateway:
            poisiongateway = 'True'

        self.poision_gateway_info = tk.Label(right_frame_info, text=poisiongateway)
        self.poision_gateway_info.grid(column=1, row=4, sticky='W')

        # hwsrc info
        tk.Label(left_frame_info, text='hwsrc mac: ').grid(column=0, row=5, sticky='E')

        self.hwsrc_info = tk.Label(right_frame_info, text=self.savedsettings.hwsrc)
        self.hwsrc_info.grid(column=1, row=5, sticky='W')

        # time interval
        tk.Label(left_frame_info, text='time interval: ').grid(column=0, row=6, sticky='E')

        self.time_interval_info = tk.Label(right_frame_info, text=self.savedsettings.time_interval)
        self.time_interval_info.grid(column=1, row=6, sticky='W')

        logging.info('building gui finished')
        self.root.mainloop()

    def reload_setting_ui(self):
        # reload setting ui with the new setting
        self.my_mac_info.configure(text=self.savedsettings.this_pc_mac)
        self.gateway_mac_info.configure(text=self.savedsettings.gateway_mac)
        self.gateway_ip_info.configure(text=self.savedsettings.gateway_ip)
        self.hwsrc_info.configure(text=self.savedsettings.hwsrc)
        self.time_interval_info.configure(text=self.savedsettings.time_interval)

        poisiongateway = 'False'
        if self.savedsettings.poision_gateway:
            poisiongateway = 'True'
        self.poision_gateway_info.configure(text=poisiongateway)
