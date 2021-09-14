import sys
sys.path.append(r'C:\Users\zyh\Desktop\PYPOWER-master\pypower')
import case39
from runpf import runpf
import numpy as np 


def init_case(case39):
    copied_case39 = case39.copy()
    for i in range(copied_case39['branch'].shape[0]):
        copied_case39['branch'][i,3] *= 1.5
    for i in range(32,35):
        copied_case39['bus'][i,1] = 1
    for i in range(0,10):
        copied_case39['gen'][i,1] *= 0.5
    wind_buses = [3,4,5,6,12,13,14,15,16,17,18,27]
    for wind_bus in wind_buses:
        copied_case39['gen']=np.vstack((copied_case39['gen'],np.array(
            [[wind_bus,262.41,80,999,-999,1,100,1,999,0,0,0,0,0,0,0,0,0,0,0,0],])))
        copied_case39['gencost']=np.vstack((copied_case39['gencost'],copied_case39['gencost'][0,:]))
    
    copied_case39['gen'][i,2] -= 96
    copied_case39['gen'][16,2] = -10
    copied_case39['gen'][17,2] = 0
    copied_case39['gen'][18,2] = 0
    copied_case39['gen'][10,2] = -20
    copied_case39['gen'][11,2] += 30
    copied_case39['gen'][12,2] += 30
    copied_case39['gen'][13,2] += 30
    copied_case39['gen'][14,2] += 30
    copied_case39['gen'][15,2] += 30
    copied_case39['bus'][:,7] = 1
    copied_case39['gen'][:,5] = 1
    
    return copied_case39
    
    
a=case39.case39()
inited_a = init_case(a)
x=runpf(inited_a)[0]