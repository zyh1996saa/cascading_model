import sys
sys.path.append(r'.\PYPOWER-master\pypower')
import case39
from runpf import runpf
import numpy as np 
import time
import random


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
    copied_case39['gen'][10,2] = 20
    copied_case39['gen'][11,2] += 60
    copied_case39['gen'][12,2] += 70
    copied_case39['gen'][13,2] += 80
    copied_case39['gen'][14,2] += 80
    copied_case39['gen'][15,2] += 30
    copied_case39['bus'][:,7] = 1
    copied_case39['gen'][:,5] = 1
    
    return copied_case39
    
class Cascasding_39model():
    def __init__(self):
        self.init_case = runpf(init_case(case39.case39()))[0]
        self.set_mapping()
        self.K = 0.7
        self.repeat_num = 1
        self.wind_buses = [3,4,5,6,12,13,14,15,16,17,18,27]
    
    def set_mapping(self):
        self.mapping = {}
        for i in range(self.init_case['bus'].shape[0]):
            for j in range(self.init_case['gen'].shape[0]):
                if int(self.init_case['gen'][j,0]) == int(self.init_case['bus'][i,0]) and j>9:
                    self.mapping[str(i)] = j
        
    def set_short_fault(self,case,buses):
        cp_case = case.copy()
        for i in buses:
            cp_case['gen'][int(self.mapping[str(i-1)]),2] = self.K*cp_case['gen'][int(self.mapping[str(i-1)]),1]
            cp_case['gen'][int(self.mapping[str(i-1)]),1] = 0
        return cp_case
    
    def check_if_new_bus_over_V(self,bef_case,cur_case):
        bef_buses,cur_buses = [],[]
        for i in range(bef_case['bus'].shape[0]):
            if bef_case['bus'][i,7] >= 1.1:
                bef_buses.append(i)
            if cur_case['bus'][i,7] >= 1.1:
                cur_buses.append(i)
        for i in cur_buses :
            if i not in bef_buses:
                return True
        return False 
    
    def cut_P_by_voltage(self,case):
        cp_case = case.copy()
        cp_init_case = self.init_case.copy()
        bef_cut_Pall = cp_case['gen'][:,1].sum()
        for i in range(cp_case['bus'].shape[0]):
            temp_V_i = cp_case['bus'][i,7]

            if temp_V_i>=1.1 and (i+1 in self.wind_buses) and(i+1 not in self.cur_fault):
                cut_wind_num = 0
                temp_gen_num = int(self.mapping[str(i)])
                for j in range(87):
                    random_num = random.uniform(1.1,1.2)
                    if temp_V_i>random_num:
                        cut_wind_num += 1
                if cp_init_case['gen'][temp_gen_num,1]-cp_case['gen'][temp_gen_num,1] <= 3*cut_wind_num:
                    cp_case['gen'][temp_gen_num,1] = cp_init_case['gen'][temp_gen_num,1] - 3*cut_wind_num
                    cp_case['gen'][temp_gen_num,2] = cp_init_case['gen'][temp_gen_num,2] + self.K*3*cut_wind_num
                else:
                    pass
        after_cut_Pall = cp_case['gen'][:,1].sum()
        k = after_cut_Pall/bef_cut_Pall
        for i in range(cp_case['bus'].shape[0]):
            cp_case['bus'][i,2] = cp_init_case['bus'][i,2] * k
        return cp_case
         
    def run(self):
        short_fault_set = [[12,13]]
        fault_count = 0
        self.write_initcase()
        for short_fault in short_fault_set:
            fault_count += 1
            self.cur_fault = short_fault.copy()
            for repeat_time in range(self.repeat_num):
                chain_count = 0 
                begin_case = self.set_short_fault(self.init_case,short_fault)
                bef_case = begin_case.copy()
                begin_case = runpf(begin_case)[0]
                cur_case = begin_case.copy()
                
                while self.check_if_new_bus_over_V(bef_case,cur_case):
                    chain_count += 1
                    bef_case = cur_case
                    cur_case = self.cut_P_by_voltage(cur_case)
                    cur_case = runpf(cur_case)[0]
        return begin_case

    def write_initcase(self):
        with open('init_case.csv','a') as f:
            f.write('fault_num,repeat_num,chain_num,')
            f.write(','.join(['Vbus%s'%i for i in range(1,self.init_case['bus'].shape[0]+1)]))
            f.write(',')
            f.write(','.join(['Angbus%s'%i for i in range(1,self.init_case['bus'].shape[0]+1)]))
            f.write(',')
            f.write(','.join(['Pbus%s'%i for i in range(1,13)]))
            f.write(',')
            f.write(','.join(['Qbus%s'%i for i in range(1,13)]))
            f.write('\n')
            
def run():
    model_39 = Cascasding_39model()
    model_39.run()

if __name__ == '__main__':
    run()