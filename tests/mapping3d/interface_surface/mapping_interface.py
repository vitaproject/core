
import time
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import brentq
import scipy.integrate as integrate
from scipy.interpolate import interp1d
from raysect.core import Point2D, Point3D, World, rotate_z
from raysect.primitive import import_ply
from cherab.tools.equilibrium import plot_equilibrium

from vita.modules.sol_heat_flux.eich import Eich
from vita.modules.cherab import FieldlineTracer, RK2, InterfaceSurface, sample_power_at_surface
from vita.modules.fiesta import Fiesta
from vita.utility import get_resource


# the world scene-graph
world = World()


##########################
# add machine components #
meshes = {}

vessel = get_resource("ST40-IVC2", "mesh", "vessel")
vessel = import_ply(vessel, scaling=0.001, parent=world, name="vessel")
meshes["vessel"] = vessel

vessel_lower = get_resource("ST40-IVC2", "mesh", "vessel_lower")
vessel_lower = import_ply(vessel_lower, scaling=0.001, parent=world, name="vessel_lower")
meshes["vessel_lower"] = vessel_lower

vessel_upper = get_resource("ST40-IVC2", "mesh", "vessel_upper")
vessel_upper = import_ply(vessel_upper, scaling=0.001, parent=world, name="vessel_upper")
meshes["vessel_upper"] = vessel_upper

centre_column = get_resource("ST40-IVC2", "mesh", "centre_column")
centre_column = import_ply(centre_column, scaling=0.001, parent=world, name="centre_column")
meshes["centre_column"] = centre_column

poloidal_coil_lower_45 = get_resource("ST40-IVC2", "mesh", "poloidal_coil_lower_45")
poloidal_coil_lower_45 = import_ply(poloidal_coil_lower_45, scaling=0.001, name="poloidal_coil_lower_45")
meshes["poloidal_coil_lower_45"] = poloidal_coil_lower_45
for i in range(8):
    poloidal_coil_lower_45.instance(parent=world, transform=rotate_z(i * 45), name="poloidal_coil_lower_45")

poloidal_coil_upper_45 = get_resource("ST40-IVC2", "mesh", "poloidal_coil_upper_45")
poloidal_coil_upper_45 = import_ply(poloidal_coil_upper_45, scaling=0.001, name="poloidal_coil_upper_45")
meshes["poloidal_coil_upper_45"] = poloidal_coil_upper_45
for i in range(8):
    poloidal_coil_upper_45.instance(parent=world, transform=rotate_z(i * 45), name="poloidal_coil_upper_45")

limiter_lower_45 = get_resource("ST40-IVC2", "mesh", "limiter_lower_45")
limiter_lower_45 = import_ply(limiter_lower_45, scaling=0.001, name="limiter_lower_45")
meshes["limiter_lower_45"] = limiter_lower_45
for i in range(8):
    limiter_lower_45.instance(parent=world, transform=rotate_z(i * 45), name="limiter_lower_45")

limiter_upper_45 = get_resource("ST40-IVC2", "mesh", "limiter_upper_45")
limiter_upper_45 = import_ply(limiter_upper_45, scaling=0.001, name="limiter_upper_45")
meshes["limiter_upper_45"] = limiter_upper_45
for i in range(8):
    limiter_upper_45.instance(parent=world, transform=rotate_z(i * 45), name="limiter_upper_45")

divertor_tile_lower_45 = get_resource("ST40-IVC2", "mesh", "divertor_tile_lower_45")
divertor_tile_lower_45 = import_ply(divertor_tile_lower_45, scaling=0.001, name="divertor_tile_lower_45")
meshes["divertor_tile_lower_45"] = divertor_tile_lower_45
for i in range(8):
    divertor_tile_lower_45.instance(parent=world, transform=rotate_z(i * 45), name="divertor_tile_lower_45")

divertor_tile_upper_45 = get_resource("ST40-IVC2", "mesh", "divertor_tile_upper_45")
divertor_tile_upper_45 = import_ply(divertor_tile_upper_45, scaling=0.001, name="divertor_tile_upper_45")
meshes["divertor_tile_upper_45"] = divertor_tile_upper_45
for i in range(8):
    divertor_tile_upper_45.instance(parent=world, transform=rotate_z(i * 45), name="divertor_tile_upper_45")

centre_column_tiles_lower_45 = get_resource("ST40-IVC2", "mesh", "centre_column_tiles_lower_45")
centre_column_tiles_lower_45 = import_ply(centre_column_tiles_lower_45, scaling=0.001, name="centre_column_tiles_lower_45")
meshes["centre_column_tiles_lower_45"] = centre_column_tiles_lower_45
for i in range(8):
    centre_column_tiles_lower_45.instance(parent=world, transform=rotate_z(i * 45), name="centre_column_tiles_lower_45")

centre_column_tiles_upper_45 = get_resource("ST40-IVC2", "mesh", "centre_column_tiles_upper_45")
centre_column_tiles_upper_45 = import_ply(centre_column_tiles_upper_45, scaling=0.001, name="centre_column_tiles_upper_45")
meshes["centre_column_tiles_upper_45"] = centre_column_tiles_upper_45
for i in range(8):
    centre_column_tiles_upper_45.instance(parent=world, transform=rotate_z(i * 45), name="centre_column_tiles_upper_45")


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



