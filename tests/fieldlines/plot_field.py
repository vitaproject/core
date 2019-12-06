
import matplotlib.pyplot as plt

from vita.modules.fiesta import Fiesta
from vita.utility import get_resource

from cherab.tools.equilibrium import plot_equilibrium


# load the equilibrium
eq002 = get_resource("ST40", "equilibrium", "eq002")
fiesta = Fiesta("eq_0002_test.mat")
equilibrium = fiesta.to_cherab_equilibrium()

plt.ion()
plot_equilibrium(equilibrium, detail=True)
plt.show()
