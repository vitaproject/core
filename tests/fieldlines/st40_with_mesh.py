
import numpy as np
from mayavi import mlab
from raysect.core import Point3D, World
from raysect.primitive import import_obj

from vita.modules.cherab import FieldlineTracer, RK2
from vita.modules.fiesta import Fiesta
from vita.utility import get_resource


# the world scene-graph
world = World()
ST40_mesh = get_resource("ST40", "mesh", "ST40_IVC")
import_obj(ST40_mesh, scaling=0.001, parent=world)


eq001 = get_resource("ST40", "equilibrium", "limited_eq001_export")
fiesta = Fiesta(eq001)
b_field = fiesta.b_field


seed_points = []

n = 20
for i in range(n):
    lcfs = 0.72677891
    seed_points.append(Point3D(lcfs + i*0.001, 0.0, 0.0 + 0.02))
        
        #Point3D(0.7270, 0, 0),
        #Point3D(0.7275, 0, 0),
        #Point3D(0.7280, 0, 0)]


field_tracer = FieldlineTracer(b_field, method=RK2(step_size=0.00005))

end_points = []
trajectories = []
for i in range(n):
    end_point, _, trajectory = field_tracer.trace(world, seed_points[i], save_trajectory=True, max_length=10)
    trajectories.append(trajectory)
    end_points.append(end_point)

# mlab.plot3d([0, 0.005, 0.001], [0, 0, 0], [0, 0, 0], tube_radius=0.0005, color=(1, 0, 0))
# mlab.plot3d([0, 0, 0], [0, 0.005, 0.001], [0, 0, 0], tube_radius=0.0005, color=(0, 1, 0))
# mlab.plot3d([0, 0, 0], [0, 0, 0], [0, 0.005, 0.001], tube_radius=0.0005, color=(0, 0, 1))


from raysect_mayavi import visualise_scenegraph
visualise_scenegraph(world)

for i in range(n):
    mlab.plot3d(trajectories[i][:, 0], trajectories[i][:, 1], trajectories[i][:, 2], tube_radius=0.0005)#) color=(1, 0, 0))
    savename = 'fieldline' + str(i) + '.csv'
    np.savetxt(savename, (trajectories[i][:, 0], trajectories[i][:, 1], trajectories[i][:, 2]), delimiter=',')
#mlab.plot3d(trajectory2[:, 0], trajectory2[:, 1], trajectory2[:, 2], tube_radius=0.0005, color=(0.5, 0.5, 0))
#mlab.plot3d(trajectory3[:, 0], trajectory3[:, 1], trajectory3[:, 2], tube_radius=0.0005, color=(0, 1, 0))
#mlab.plot3d(trajectory4[:, 0], trajectory4[:, 1], trajectory4[:, 2], tube_radius=0.0005, color=(0, 0, 1))

#np.savetxt('fieldline1.csv', (trajectory1[:, 0], trajectory1[:, 1], trajectory1[:, 2]), delimiter=',')
#np.savetxt('fieldline2.csv', (trajectory2[:, 0], trajectory2[:, 1], trajectory2[:, 2]), delimiter=',')
#np.savetxt('fieldline3.csv', (trajectory3[:, 0], trajectory3[:, 1], trajectory3[:, 2]), delimiter=',')
#np.savetxt('fieldline4.csv', (trajectory4[:, 0], trajectory4[:, 1], trajectory4[:, 2]), delimiter=',')


