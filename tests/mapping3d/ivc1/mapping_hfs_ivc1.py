
import numpy as np
from raysect.core import Point2D, World

from vita.modules.sol_heat_flux.eich.eich import Eich
from vita.modules.cherab import FieldlineTracer, RK2, RK4, InterfaceSurface, sample_power_at_surface
from vita.modules.cherab import load_wall_configuration
from vita.modules.equilibrium.fiesta import Fiesta
from vita.utility import get_resource


# the world scene-graph
world = World()


##########################
# add machine components #

config_file = get_resource("ST40-IVC1", "configuration", 'st40_ivc1_config')
load_wall_configuration(config_file, world)


########################
# load the equilibrium #
eq007 = get_resource("ST40-IVC1", "equilibrium", "div_007")
fiesta = Fiesta(eq007)
b_field = fiesta.b_field
field_tracer = FieldlineTracer(b_field, method=RK2(step_size=0.0001))
equilibrium = fiesta.to_cherab_equilibrium()
psin2d = equilibrium.psi_normalised


##############################
# setup the heatflux profile #

# specify and load heatflux profile
# footprint = Eich(3, 0.0001)  # lambda_q=2.5, S=0.5
#
# x = np.linspace(-1, 10, 100)
# footprint.set_coordinates(x)
# footprint.s_disconnected_dn_max = 2.1
# footprint.fx_in_out = 5.
# footprint.calculate_heat_flux_density("lfs")

# # LFS interface
# POINT_A = Point2D(0.345941, -0.593439)
# POINT_B = Point2D(0.51091, -0.757166)
# power_profile = sample_power_at_surface(POINT_A, POINT_B, equilibrium, footprint, side="LFS")
# interface_power = 1e6  # 1MW
# angle_period = 45
#
# interface_surface = InterfaceSurface(POINT_A, POINT_B, power_profile, interface_power)
# interface_surface.map_power(interface_power, angle_period, field_tracer, world,
#                             num_of_fieldlines=5000, phi_offset=-angle_period/2, debug_output=True)


# HFS mapping
r0_hfs = fiesta.get_midplane_lcfs()[0]
r0_lfs = fiesta.get_midplane_lcfs()[1]
footprint = Eich(1, 0.0001, r0_lfs=r0_lfs, r0_hfs=r0_hfs)  # lambda_q=2.5, S=0.5

x = np.linspace(-1, 10, 100)
footprint.set_coordinates(x)
footprint.s_disconnected_dn_max = 2.1
footprint.fx_in_out = 5.
footprint.calculate_heat_flux_density("hfs")

field_tracer = FieldlineTracer(b_field, method=RK4(step_size=0.0001, direction="negative"))

# HFS interface
POINT_A = Point2D(0.25, -0.5)
POINT_B = Point2D(0.3304, -0.5833)
power_profile = sample_power_at_surface(POINT_A, POINT_B, equilibrium, footprint,
                                        lcfs_radii_min=0.15, lcfs_radii_max=0.25, side="HFS")

interface_power = 5e5  # 0.5MW
angle_period = 45

interface_surface = InterfaceSurface(POINT_A, POINT_B, power_profile, interface_power)
interface_surface.map_power(interface_power, angle_period, field_tracer, world,
                            num_of_fieldlines=5000, phi_offset=-angle_period/2, debug_output=True)
interface_surface.poloidal_trajectory_plot(field_tracer, world, equilibrium)