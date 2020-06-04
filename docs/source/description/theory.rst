
******
Theory
******

==================================
Objectives, formulation and models
==================================

In order to provide the functionality needed, each of the tools tackles one specific phase. As opposed to a typical
analysis workflow, the main objective is maximizing the final user's productivity. Their design therefore hides any
numerical complexity, and allows their operation using machine and experimental parameters. Several models are
provided as a black-box, which is previously validated by analyst experts, but its source code can be inspected,
audited, and extended at any time.

The formulation used for this first implementation is based on the thermal equilibrium using the Principle of
Virtual Power. The contributions to the power virtual variation, :math:`\\delta \\dot \\Pi`, are calculated from the
numerical integration of the following residual equation:

.. math::
   \\delta \\dot \\Pi = \\delta \\dot \\Pi_{capacitance} - \\delta \\dot \\Pi_{external} - \\delta \\dot \\Pi_{conduction} = 0

Each of the previous contribution terms can be expressed in the reference configuration \cite{Iglesias2015} as:

.. math::
   \\delta \\dot \\Pi_{capacitance} & = & \\int_{\\mathcal B} \\rho c_p \\frac{dT}{dt} \\delta T \ dV

.. math::
   \\delta \\dot \\Pi_{external} & = & \\int_{\\mathcal \\partial B} \\bs q \\delta T \\cdot \\bs n \ dS

.. math::
   \\delta \\dot \\Pi_{conduction} & = & \\int_{\\mathcal B} \\left( \\bs \\kappa \\nabla T \\right) \\cdot \\nabla \\delta T \ dV

Where the conductivity tensor :math:`\\bs \\kappa` and the specific heat capacity :math:`c_p`, are temperature
dependent, :math:`f(T)`, properties of the material. The density :math:`\rho` is considered constant.

.. _fig-scheme-software:

.. figure:: figures/scheme_software.png
   :align: center
   :width: 650px

   3D CAD (left) and 2D numerical discretization (right) of divertor components: Tile 5 (top) and tile 6 (bottom).

Fully nonlinear Finite Element (FE) approximations are used for all analyses, with some Galerkin meshfree
enhancements [Iglesias2013]_ when applicable. Several de-featuring levels are applied when speed is a concern.
Initial implementation uses 2D models shown in :numref:`fig-scheme-software`, but design is extensible to 3D
in the future. Orthotropic effects, as well as Planck radiation or convection cooling are also foreseen.

Coatings and deposits can be modelled with exact properties, by means of a proper layer formulation which is
available for all the applications. Usual parameters for the JET divertor tiles range from 10 - 20 um thickness for
the W coating on CFC tiles, to 50 um node separation in direction normal to the surface for modelling ELMs
accurately in bulk W tiles.
