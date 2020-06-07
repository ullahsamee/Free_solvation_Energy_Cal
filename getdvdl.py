import math
from collections import OrderedDict


class OnlineAvVar(object):
    def __init__(self, store_data = False):
        self.step = 0
        self.mean = 0.0
        self.M2 = 0.0

        self.store = store_data
        self.data = []


    def accumulate(self, x):
        
  

        self.step += 1

        delta = x - self.mean

        self.mean += delta / self.step
        self.M2 += delta * (x - self.mean)

        if self.store:
            self.data.append(x)


    def get_variance(self):
    

        return self.M2 / (self.step - 1)


    def get_stat(self):
    

        return self.mean, math.sqrt(self.M2 / (self.step - 1))

if __name__ == '__main__':
    
    import os, sys, glob
    import numpy as np



    prog = sys.argv[0]

    if len(sys.argv) < 4:
       
        sys.exit(1)

    skip = int(sys.argv[1])
    glob_pattern = sys.argv[2]
    windows = sys.argv[3:]
    
    extrap = 'polyfit' # or linear or polyfit
    stats = []

    data = OrderedDict()

    for window in windows:
        cwd = os.getcwd()
        os.chdir(window)
        dVdl = OnlineAvVar()    
        ln = 0

        for en in glob.glob(glob_pattern):
            
            with open(en, 'r') as en_file:
                for line in en_file:
                    ln += 1
                    if "NaN" in line:
                        print("NaN found in this dir: ", os.getcwd())

                    if ln > skip and line.startswith('L9') and not 'dV/dlambda' in line and "NaN" not in line:
                        #print(float(line.split()[5]))
                        dVdl.accumulate(float(line.split()[5]) )

        mean, std = dVdl.get_stat()
  
        data[float(window)] = (mean, std / math.sqrt(dVdl.step), std)

        os.chdir(cwd)

    x = [i for i in data.keys()]
    y = [d[0] for d in data.values()]
    print("x=")
    print(x)
    print("y=")
    print(y)

    if extrap == 'linear':
        if 0.0 not in x:
            l = (x[0]*y[1] - x[1]*y[0]) / (x[0] - x[1])
            x.insert(0, 0.0)
            y.insert(0, l)

    if 1.0 not in x:
        l = ( (x[-2] - 1.0)*y[-1] + ((1.0-x[-1])*y[-2]) ) / (x[-2] - x[-1])
        x.append(1.0)
        y.append(l)
    elif extrap == 'polyfit' and (0.0 not in x or 1.0 not in x):
        if len(x) < 6:
            deg = len(x) - 1
        else:
            deg = 6

        coeffs = np.polyfit(x, y, deg)

        if 0.0 not in x:
            x.insert(0, 0.0)
            y.insert(0, coeffs[-1])

        if 1.0 not in x:
            x.append(1.0)
            y.append(sum(coeffs) )

    for a, b in zip(x, y):
        if a in data:
            v = data[a]
            print(a, v[0], v[1], v[2])
        else:
            print(a, b)

    print('# dG =', np.trapz(y, x))

