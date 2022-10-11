import logging
import os

from data_manager import datamanager
from gui import gui

# @author:- kaleab nigusse

log = logging.basicConfig(filename="log.txt", level=logging.DEBUG, format="%(asctime)s %(message)s")

data_mgr = datamanager()
ui = gui(data_mgr)
ui.build_gui()