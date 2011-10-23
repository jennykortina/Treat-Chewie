import os; import appscript; import time

def make_call(phone_number):
    os.popen('open facetime://%s' % phone_number)
    appscript.app('FaceTime').activate(); time.sleep(2); appscript.app('System Events').keystroke('\r')
