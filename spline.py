import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
x = [1,5,10,30,45,100]
y = [1,3,40,4,50,3]
f = interp1d(x, y)
f2 = interp1d(x, y, kind='cubic')



xnew = range(x[0], x[-1])

import matplotlib.pyplot as plt
plt.plot(x,y,'o',xnew,f(xnew),'-', xnew, f2(xnew),'--')
plt.legend(['data', 'linear', 'cubic'], loc='best')
plt.show()
