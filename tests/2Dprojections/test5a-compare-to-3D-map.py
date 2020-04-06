
import numpy as np
import matplotlib.pyplot as plt
from raysect.core import Point2D

from vita.modules.sol_heat_flux.eich.eich import Eich
from vita.modules.equilibrium.fiesta import Fiesta
from vita.modules.projection.projection2D.psi_map_projection import map_psi_omp_to_divertor
from vita.utility import get_resource

def sample_power_at_surface(point_a, point_b, fiesta, footprint):
    x_axis = footprint.get_global_coordinates()
    divertor_coords_x = np.array((point_a[0], point_b[0]))
    divertor_coords_y = np.array((point_a[1], point_b[1]))
    divertor_coords = np.array([divertor_coords_x, divertor_coords_y])
    divertor_map = map_psi_omp_to_divertor(x_axis, divertor_coords, fiesta)
    
    r_div = np.array([divertor_map[i]["R_pos"] for i in x_axis])
    z_div = np.array([divertor_map[i]["Z_pos"] for i in x_axis])
    angles = np.array([divertor_map[i]["alpha"] for i in x_axis])
    fx = np.array([divertor_map[i]["f_x"] for i in x_axis])

    power = x_axis*footprint._q/(r_div*(fx/np.cos(angles)))
    
    return [r_div, z_div, power]

##########################
# add machine components #

config_file = get_resource("ST40-IVC1", "configuration", 'st40_ivc1_config')


########################
# load the equilibrium #
eq = get_resource("ST40-IVC1", "equilibrium", "eq_006_2T_export")
fiesta = Fiesta(eq)

##############################
# setup the heatflux profile #

# specify and load heatflux profile
lcfs = fiesta.get_midplane_lcfs(psi_p = 1.00001)[1]
footprint = Eich(1.0e-3, 0.0001e-3, r0_lfs=lcfs)  # lambda_q=2.5, S=0.5

x = np.linspace(-1, 10, 100)*1e-3
footprint.set_coordinates(x)
footprint.calculate_heat_flux_density("lfs")

POINT_A = Point2D(0.345941, -0.593439)
POINT_B = Point2D(0.51091, -0.757166)
power_profile = sample_power_at_surface(POINT_A, POINT_B, fiesta, footprint)
s = np.sqrt(power_profile[0]**2 + power_profile[1]**2) - np.sqrt(POINT_A[0]**2 + POINT_A[1]**2)
plt.plot(s, power_profile[2]/max(power_profile[2])*40)
