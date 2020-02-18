
import numpy as np
from raysect.core import Point2D, World

from vita.modules.sol_heat_flux.eich import Eich
from vita.modules.cherab import FieldlineTracer, RK2, InterfaceSurface, sample_power_at_surface
from vita.modules.cherab import load_wall_configuration
from vita.modules.fiesta import Fiesta
from vita.utility import get_resource


# the world scene-graph
world = World()


##########################
# add machine components #

config_file = get_resource("ST40-IVC2", "configuration", 'st40_ivc2_config')
load_wall_configuration(config_file, world)


########################
# load the equilibrium #
eq002 = get_resource("ST40", "equilibrium", "eq002")
fiesta = Fiesta(eq002)
b_field = fiesta.b_field
field_tracer = FieldlineTracer(b_field, method=RK2(step_size=0.0001))
equilibrium = fiesta.to_cherab_equilibrium()
psin2d = equilibrium.psi_normalised


##############################
# setup the heatflux profile #

# specify and load heatflux profile
footprint = Eich(2.5, 0.5)  # lambda_q=2.5, S=0.5

x = np.linspace(-1, 10, 100)
footprint.set_coordinates(x)
footprint.s_disconnected_dn_max = 2.1
footprint.fx_in_out = 5.
footprint.calculate_heat_flux_density("lfs")

POINT_A = Point2D(0.44, -0.79)
POINT_B = Point2D(0.57, -0.798)
power_profile = sample_power_at_surface(POINT_A, POINT_B, equilibrium, footprint)
interface_power = 1e6  # 1MW
angle_period = 45

interface_surface = InterfaceSurface(POINT_A, POINT_B, power_profile, interface_power)
interface_surface.map_power(interface_power, angle_period, field_tracer, world,
                            num_of_fieldlines=100, debug_output=True)
