
import numpy as np
import scipy.integrate as integrate
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt

from vita.modules.sol_heat_flux.eich import Eich


footprint = Eich(2.5, 0.5)  # lambda_q=2.5, S=0.5

x = np.linspace(-1, 10, 100)
footprint.set_coordinates(x)
footprint.s_disconnected_dn_max = 2.1
footprint.fx_in_out = 5.
footprint.calculate_heat_flux_density("lfs")

# sampling power function outside LCFS
s_vals = np.linspace(0, 10, 1000)
q_vals = np.array([footprint(s) for s in s_vals])

integral = integrate.simps(q_vals, s_vals)
q_vals /= integral

ds = s_vals[1] - s_vals[0]
q_cumulative_values = []
for i in range(q_vals.shape[0]):
    if i == 0:
        q_cumulative_values.append(0)
    else:
        q_cumulative_values.append(q_cumulative_values[i-1] + (q_vals[i] * ds))

print("integral")
print(integrate.simps(q_vals, s_vals))

plt.ion()
plt.plot(s_vals, q_vals)

plt.figure()
plt.plot(q_cumulative_values, s_vals)

q_to_s_func = interp1d(q_cumulative_values, s_vals, fill_value="extrapolate")



