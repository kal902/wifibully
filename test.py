import threading
class a:
    def __init__(self):
        pass

    def ss(self):
        s = b('d')
        s.j()
    

class b(threading.Thread):

    def __init__(self,dd):
        pass
    def j(self):
        print('h')
    pass

a().ss()

