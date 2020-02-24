# Installation instructions

- Install Raysect with special branch - feature/mesh_uv_points
'git clone raysect...'
cd raysect
'git checkout feature/mesh_uv_points'
'python setup.py develop'

- Install Cherab with master branch
git clone https://github.com/cherab/core.git cherab
cd cherab
git checkout master
python setup.py develop

- install VITA
python setup.py develop --include-cherab

