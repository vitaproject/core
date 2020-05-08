
import operator
import numpy as np
from math import sqrt
import matplotlib.pyplot as plt
from scipy.optimize import brentq
from raysect.core import Point2D, World
from cherab.tools.primitives import axisymmetric_mesh_from_polygon
from cherab.tools.equilibrium import plot_equilibrium

from vita.modules.sol_heat_flux.eich import Eich
from vita.modules.projection.cherab import FieldlineTracer, RK2, InterfaceSurface, sample_power_at_surface
from vita.modules.projection.cherab import load_wall_configuration
from vita.modules.equilibrium import Fiesta
from vita.utility import get_resource


# the world scene-graph
world = World()

########################
# load the equilibrium #
eq006 = get_resource("ST40-IVC1", "equilibrium", "eq_006_2T_export")
fiesta = Fiesta(eq006)
b_field = fiesta.b_field
field_tracer = FieldlineTracer(b_field, method=RK2(step_size=0.0001))
equilibrium = fiesta.to_cherab_equilibrium()
psin2d = equilibrium.psi_normalised


##############################
# setup the heatflux profile #

# specify and load heatflux profile
footprint = Eich(1.0e-3, 0.0001e-3)

x = np.linspace(-0.001, 0.01, 100)
footprint.set_coordinates(x)
footprint.s_disconnected_dn_max = 2.1
footprint.fx_in_out = 5.
footprint.calculate_heat_flux_density("lfs")
footprint.plot_heat_power_density()


# make a mesh of the interface surface
interface_point_a = Point2D(0.345941, -0.593439)
interface_point_b = Point2D(0.51091, -0.757166)
interface_vector = interface_point_a.vector_to(interface_point_b)
interface_polygon = np.zeros((100, 2))
psi_on_interface = []
for i in range(100):
    point = interface_point_a + interface_vector * i / 100
    interface_polygon[i, :] = point.x, point.y
    psi_on_interface.append(psin2d(point.x, point.y))
interface_mesh = axisymmetric_mesh_from_polygon(interface_polygon)
interface_mesh.parent = world
interface_mesh.name = "interface_mesh"

# find LCFS midplane radius
def psin(r, offset=0):
    return psin2d(r, 0) - 1 + offset
r_lcfs = brentq(psin, 0.7, 0.9, args=(0,))

midplane_point_a = Point2D(r_lcfs - 0.005, 0)
midplane_point_b = Point2D(r_lcfs + 0.05, 0)
power_profile = sample_power_at_surface(midplane_point_a, midplane_point_b, equilibrium, footprint)
interface_power = 1e6  # 1MW
angle_period = 45


plt.figure()
profile_x = np.arange(len(power_profile)) / len(power_profile) * midplane_point_a.distance_to(midplane_point_b)
plt.plot(profile_x, power_profile)
plt.xlabel('Midplane interface distance (m)')
plt.title("Input power profile to ray tracing")

midplane_surface = InterfaceSurface(midplane_point_a, midplane_point_b, power_profile, interface_power)

mapping_results = midplane_surface.map_power(interface_power, angle_period, field_tracer, world,
                                             num_of_fieldlines=20000, debug_output=True, write_output=False,
                                             debug_count=1000)
_, mesh_hitpoints, mesh_seedpoints = mapping_results

hitpoints = np.array(mesh_hitpoints["interface_mesh"])
seedpoints = np.array(mesh_seedpoints["interface_mesh"])

hit_point_distribution = []
for i in range(hitpoints.shape[0]):

    x, y, z = hitpoints[i]
    r = sqrt(x**2 + y**2)
    p = Point2D(r, z)
    x_dist = interface_point_a.distance_to(p)
    hit_point_distribution.append(x_dist)

fig, ax = plt.subplots()
interface_distance = interface_point_a.distance_to(interface_point_b)
n, bins, patches = ax.hist(hit_point_distribution, 50, range=[0, interface_distance], density=1)
ax.set_xlabel('Interface distance (m)')
ax.set_ylabel('Hit point density')
ax.set_title('Ray traced hit point distribution along interface surface')

# other method
power_profile = sample_power_at_surface(interface_point_a, interface_point_b, equilibrium, footprint)
interface_power = 1e6  # 1MW
angle_period = 45

interface_surface = InterfaceSurface(interface_point_a, interface_point_b, power_profile, interface_power)
interface_surface.histogram_plot()

plt.figure()
plt.plot(psi_on_interface)
plt.title('PSI along divertor interface')

plot_equilibrium(equilibrium, detail=False)
plt.plot([interface_point_a.x, interface_point_b.x], [interface_point_a.y, interface_point_b.y], 'k')


# TODO - Jeppe could insert his calculation method here, allowing comparison within the same script.


# find and plot the peak of the histogram
index, value = max(enumerate(n), key=operator.itemgetter(1))
peak_position = (bins[index] + bins[index+1])/2
peak_point2d = interface_point_a + interface_vector.normalise() * peak_position
plt.plot([peak_point2d.x], [peak_point2d.y], 'r.')

# # add jeppes peak position
# jeppes_peak_position = 0.02  JEPPE - add your peak position here for the plots
# peak_point2d = interface_point_a + interface_vector.normalise() * peak_position
# plt.plot([peak_point2d.x], [peak_point2d.y], 'g.')


# for saving output distributions
num_samples = 10000
isf = interface_surface
mapped_distribution = []
for i in range(num_samples):
    sample = isf._generate_sample_point()
    x = isf._point_a.distance_to(sample)
    mapped_distribution.append(x)

data = {
    'ray_traced': hit_point_distribution,
    'psi_mapped': mapped_distribution
}


import pickle
with open('Matt_eq006_2T_data.pickle', 'wb') as fh:
    pickle.dump(data, fh)


