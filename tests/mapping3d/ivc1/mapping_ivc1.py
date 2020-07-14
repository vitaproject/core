
import numpy as np
from raysect.core import Point2D, World

from vita.modules.sol_heat_flux.eich import Eich
from vita.modules.projection.cherab import FieldlineTracer, RK2, InterfaceSurface, sample_power_at_surface
from vita.modules.projection.cherab import load_wall_configuration
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
eq007 = get_resource("ST40-IVC1", "equilibrium", "eq_006_2T_export")
fiesta = Fiesta(eq007)
b_field = fiesta.b_field
field_tracer = FieldlineTracer(b_field, method=RK2(step_size=0.0001))
equilibrium = fiesta.to_cherab_equilibrium()
psin2d = equilibrium.psi_normalised


##############################
# setup the heatflux profile #

# specify and load heatflux profile
footprint = Eich(2.5E-3, 0.0001E-3)  # lambda_q=2.5, S=0.5

x = np.linspace(-1, 10, 100)*1E-3
footprint.set_coordinates(x)
footprint.s_disconnected_dn_max = 2.1
footprint.fx_in_out = 5.
footprint.calculate_heat_flux_density("lfs")

POINT_A = Point2D(0.340, -0.600)
POINT_B = Point2D(0.500, -0.810)
power_profile = sample_power_at_surface(POINT_A, POINT_B, equilibrium, footprint)
interface_power = 1e6  # 1MW
angle_period = 45

interface_surface = InterfaceSurface(POINT_A, POINT_B, power_profile, interface_power)
# new function
interface_surface.histogram_plot()

interface_surface.map_power(interface_power, angle_period, field_tracer, world,
                            num_of_fieldlines=30000, phi_offset=-angle_period/2-5, debug_output=True)
