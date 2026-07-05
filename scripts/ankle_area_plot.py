import numpy as np
import matplotlib.pyplot as plt

x = []
y = []

with open("ankle_area.csv") as f:
    for line in f:
        cols = line.split()

        if len(cols) != 4:
            continue

        x.append(float(cols[1]))
        y.append(float(cols[0]))

plt.plot(x, y, ".")
plt.xlabel("x")
plt.ylabel("y")
plt.grid()
plt.show()