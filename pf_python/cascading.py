import sys
sys.path.append(r'.\PYPOWER-master\pypower')
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
    
class Cascasding_39model():
    def __init__(self):
        self.init_case = runpf(init_case(case39.case39()))[0]
        self.set_mapping()
        self.K = 0.7
    
    def set_mapping(self):
        self.mapping = {}
        for i in range(self.init_case['bus'].shape[0]):
            for j in range(self.init_case['gen'].shape[0]):
                if int(self.init_case['gen'][j,0]) == int(self.init_case['bus'][i,0]) and j>9:
                    self.mapping[str(i)] = j
        
    def set_short_fault(self,case,buses):
        cp_case = case.copy()
        for i in buses:
            cp_case['gen'][int(self.mapping[str(i)]),2] = self.K*cp_case['gen'][int(self.mapping[str(i)]),1]
            cp_case['gen'][int(self.mapping[str(i)]),1] = 0
        return cp_case
            
            
            
    def run(self):
        short_fault_set = [[15,16]]
        for short_fault in short_fault_set:
            begin_case = self.set_short_fault(self.init_case,short_fault)
            begin_case = runpf(begin_case)
        
        return begin_case



model_39 = Cascasding_39model()
b = model_39.init_case
a = runpf(model_39.init_case)[0]
xx = model_39.run()[0]