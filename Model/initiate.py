import os


def init():
    if not os.path.exists(r'C:\Program Files\gicon_automation'):
        os.mkdir(r'C:\Program Files\gicon_automation')
    if not os.path.exists(r'Support\prestado'):
        os.mkdir(r'Support\prestado')
    if not os.path.exists(r'Support\tomado'):
        os.mkdir(r'Support\tomado')
