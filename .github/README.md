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


<<<<<<< HEAD
# Actions
=======
# Actions 
>>>>>>> eddc12ab7b1956f1acce8434850d46d3482cb8db

## Fork

The use of actions in this repo makes it easy for new users to get results
immediately by:

1. Forking this repo to a new GitHub repo,

2. Making changes to the python files in the forked repo

3. Waiting for GitHub Actions to bring all the generated output svg images in
**out/** and and generated html files in **docs/** back up to date.

The new versions of the generated output files can then be viewed directly on
GitHub.


## Clone

If the new user wants to make lots of changes, they might prefer to **clone**
their **forked** repository to their own computer for faster access.  Their own
computer will need to be set up appropriately with the correct software
packages. The exact set up procedure is unambiguously described in:

    .github/workflows/vita.yml


## Pull

Eventually the new user might want to upload their changes to their forked copy
of the repo in order to merge their changes into the master copy:

    vitaProject/core

To achieve this goal the new user should push their local copy to their forked
GitHub repo.  This copy will contain generated **svg** and **html** files which
differ from those in: **vitaProject/core**. These differing files complicate
the pull request pointlessly as they will be regenerated automatically after
the pull request completes. Consequently it seems better to delete these files
instead of trying to merge them, which can be done using workflow:

    github/workflows/prepareForPullRequest.yml

This workflow only runs if there is a file:

    .github/control/prepareForPullRequest.txt

present in the repository,  The easiest way to ensure that this is the case is
to manually create such a file with some random text in it using the online
GitHub editor.  When this file is committed the relevant workflow starts in
place of the normal workflow in:

    .github/workflows/vita.yml

The file: **prepareForPullRequest.txt** is automatically deleted after a
successful run of **prepareForPullRequest.yml** so that subsequqnt pushes to
this repository will behave as normal in that it will regenerate all the output
files as usual.

Once the **prepareForPullRequest** has completed successfully, the new user can
make a pull request to have the remaining files merged with those in:

    vitaProject/core

The administrator for the this repo will then be able to review just the source
code changes on GitHub before approving the pull request.
