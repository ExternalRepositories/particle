.. image:: https://github.com/scikit-hep/particle/raw/master/docs/ParticleLogo300.png
    :target: https://github.com/scikit-hep/particle


``Particle``: PDG particle data and identification codes
========================================================

|Scikit-HEP| |PyPI version| |Conda-forge version| |Zenodo DOI|

|GitHub Actions Status: CI| |Code Coverage| |Code style: black|

|Binder|


Particle provides a pythonic interface to the `Particle Data Group <http://pdg.lbl.gov/>`_ (PDG)
particle data tables and particle identification codes,
with extended particle information and extra goodies.

The PDG defines the standard particle identification (ID) numbering scheme.
The package provides the ``PDGID`` class implementing queries on those PDG IDs.
The queries are also accessible through free standing functions mimicking,
and expanding from, the HepPID/HepPDT C++ interface.

The ``Particle`` class wraps the information in the PDG particle data tables and
provides an object-oriented interface and powerful search and look-up utilities.


Installation
------------

Install ``particle`` like any other Python package:

.. code-block:: bash

    pip install particle

or similar (use ``--user``, ``virtualenv``, etc. if you wish).


Strict dependencies
-------------------

- `Python <http://docs.python-guide.org/en/latest/starting/installation/>`_ (2.7+, 3.5+)
- `importlib_resources backport <http://importlib-resources.readthedocs.io/en/latest/>`_ if using Python < 3.7
- `attrs <http://www.attrs.org/en/stable/>`_ provides classes without boilerplate (similar to DataClasses in Python 3.7)
- `hepunits <https://github.com/scikit-hep/hepunits>`_ provides units for the Scikit-HEP packages


Changelog
---------

See the `changelog <https://github.com/scikit-hep/particle/blob/master/docs/CHANGELOG.md>`__ for a history of notable changes.


Getting started: PDG IDs
------------------------

.. code-block:: python

    >>> from particle import PDGID
    >>>
    >>> pid = PDGID(211)
    >>> pid
    <PDGID: 211>
    >>> pid.is_meson
    True
    >>> pid = PDGID(99999999)
    >>> pid
    <PDGID: 99999999 (is_valid==False)>

For convenience, all properties of the ``PDGID`` class are available as standalone functions that work on any SupportsInt (including ``Particle``):

.. code-block:: python

    >>> from particle.pdgid import is_meson
    >>>
    >>> is_meson(211)
    True

These composable functions qualifying PDG IDs make it easy to classify particles.
For the sake of example, quarkonia can be specified with the following user-defined functions:

.. code-block:: python

    >>> is_heavy_flavor = lambda x: has_charm(x) or has_bottom(x) or has_top(x)
    >>> is_quarkonium = lambda x: is_meson(x) and three_charge(x)==0 and is_heavy_flavor(x).

PDG ID literals provide (``PDGID`` class) aliases for all particles loaded, with easily recognisable names.
For example:

.. code-block:: python

    >>> from particle.pdgid import literals as lid
    >>>
    >>> lid.pi_plus
    <PDGID: 211>
    >>>
    >>> from particle.pdgid.literals import Lambda_b_0
    >>> Lambda_b_0
    <PDGID: 5122>
    >>> Lambda_b_0.has_bottom
    True

You can quickly display ``PDGID`` info from the command line with:

.. code-block:: bash

    $ python -m particle pdgid 323
    <PDGID: 323>
    A              None
    J              1.0
    L              0
    S              1
    Z              None
    abspid         323
    charge         1.0
    has_bottom     False
    ...


Similarly, classes exist to express identification codes used by MC programs,
see information on converters below.


Getting started: Particles
--------------------------

You can use a variety of methods to get particles. If you know the PDG ID number
you can get a particle directly, or you can use a search:

.. code-block:: python

    >>> from particle import Particle
    >>> Particle.from_pdgid(211)
    <Particle: name="pi+", pdgid=211, mass=139.57061 ± 0.00024 MeV>
    >>>
    >>> Particle.findall('pi')[0]
    <Particle: name="pi0", pdgid=111, mass=134.9770 ± 0.0005 MeV>

You can search for the properties using keyword arguments, which include
``pdg_name``, ``name``, ``mass``, ``width``, ``charge``, ``three_charge``, ``anti_flag``, ``rank``,
``I``, ``J``, ``G``, ``P``, ``quarks``, ``status``,
``mass_upper``, ``mass_lower``, ``width_upper``, and ``width_lower``.
You can pass a callable or an exact match for any property.
The argument ``particle`` can be set to ``True``/``False``, as well,
to limit the search to particles or antiparticles.
You can also build the search yourself with the first positional
argument, which accepts a callable that is given the particle object itself.
If the first positional argument is a string, that will match against the
particle's ``name``.  The alternative ``.find()`` *requires only one*
match returned by the search, and will throw an error if more or less than one
match is found.

Here are possible sophisticated searches:

.. code-block:: python

    >>> # Print out all particles with asymmetric decay width uncertainties
    >>> ps = Particle.findall(lambda p: p.width_lower != p.width_upper)
    >>> for p in ps:
    ...     print(p.name, p.pdgid, p.width_lower, p.width_upper)
    >>>
    >>> # Find all antiparticles with 'Omega' in the name
    >>> Particle.findall('Omega', particle=False)   # several found
    >>>
    >>> # Find all antiparticles of name=='Omega'
    >>> Particle.findall(name='Omega', particle=False)  # none found
    >>>
    >>> # Find all antiparticles of pdg_name=='Omega'
    >>> Particle.findall(pdg_name='Omega', particle=False)  # only 1, of course
    [<Particle: name="Omega~+", pdgid=-3334, mass=1672.5 ± 0.3 MeV>]
    >>>
    >>> # Find all neutral beauty hadrons
    >>> Particle.findall(lambda p: p.pdgid.has_bottom and p.charge==0)
    >>>
    >>> # Find all strange mesons with c*tau > 1 meter
    >>> from hepunits import meter
    >>> Particle.findall(lambda p: p.pdgid.is_meson and p.pdgid.has_strange and p.ctau > 1 * meter, particle=True)
    [<Particle: name="K(L)0", pdgid=130, mass=497.611 ± 0.013 MeV>,
     <Particle: name="K+", pdgid=321, mass=493.677 ± 0.016 MeV>]

Once you have a particle, any of the properties can be accessed, along with several methods.
Though they are not real properties, you can access ``is_name_barred``, and ``spin_type``.
You can also ``.invert()`` a particle.

There are lots of printing choices for particles:
``describe()``, ``programmatic_name``, ``latex_name``, ``html_name``, HTML printing outs in notebooks,
and of course ``repr`` and ``str`` support.

You can get the ``.pdgid`` from a particle, as well.
Sorting particles will put lowest ``abs(PDGID)`` first.


Particle literals provide (``Particle`` class) aliases for the particles loaded,
with easily recognisable names. For example:

.. code-block:: python

    >>> from particle import literals as lp
    >>> lp.pi_plus
    <Particle: name="pi+", pdgid=211, mass=139.57061 ± 0.00024 MeV>
    >>>
    >>> from particle.literals import Lambda_b_0
    >>> Lambda_b_0
    <Particle: name="Lambda(b)0", pdgid=5122, mass=5619.60 ± 0.17 MeV>
    >>> Lambda_b_0.J
    0.5

You can quickly search for particles from the command line with
(note: quotes may be used/needed but only double quotes work as expected on Windows):

.. code-block:: bash

    $ python -m particle search "K*0"
    <Particle: name="K*(892)0", pdgid=313, mass=895.55 ± 0.20 MeV>
    <Particle: name="K*(1680)0", pdgid=30313, mass=1718 ± 18 MeV>
    <Particle: name="K*(1410)0", pdgid=100313, mass=1421 ± 9 MeV>

If you only select one particle, either by a search or by giving the PDG ID number,
you can see more information about the particle:

.. code-block:: bash

    $ python -m particle search 311
    Name: K0             ID: 311          Latex: $K^{0}$
    Mass  = 497.611 ± 0.013 MeV
    Width = -1.0 MeV
    Q (charge)        = 0       J (total angular) = 0.0      P (space parity) = -
    C (charge parity) = ?       I (isospin)       = 1/2      G (G-parity)     = ?
        SpinType: SpinType.PseudoScalar
        Quarks: dS
        Antiparticle name: K~0 (antiparticle status: Barred)


Advanced: Loading custom tables
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can control the particle data tables if you so desire. You can append a new data table using the following syntax:

.. code-block:: python

    >>> from particle import Particle
    >>> Particle.load_table('new_particles.csv', append=True)

You can also replace the particle table entirely with ``append=False`` (the default).

If you want a non-default data file distributed with the package just proceed as follows:

.. code-block:: python

    >>> from particle import data
    >>> Particle.load_table(data.basepath / "particle2018.csv"))
    >>> Particle.load_table(data.basepath / "nuclei2020.csv"), append=True)  # I still want nuclei info
    >>> Particle.table_names()  # list the loaded tables


Advanced: Conversion
^^^^^^^^^^^^^^^^^^^^

You can convert and update the particle tables with the utilities in ``particle.particle.convert``. This requires the
``pandas`` package, and is only tested with Python 3. Run the following command for more help:

.. code-block:: bash

    $ python3 -m particle.particle.convert --help


Getting started: Converters
---------------------------

You can use mapping classes to convert between particle MC identification codes
and particle names. See the ``particle.converters`` modules for the available
mapping classes. For example:

.. code-block:: python

    >>> from particle.converters import Pythia2PDGIDBiMap
    >>> from particle import PDGID, PythiaID
    >>>
    >>> pyid = Pythia2PDGIDBiMap[PDGID(9010221)]
    >>> pyid
    <PythiaID: 10221>

    >>> pdgid = Pythia2PDGIDBiMap[PythiaID(10221)]
    >>> pdgid
    <PDGID: 9010221>

This code makes use of classes similar to ``PDGID``, which hold
particle identification codes used by MC programs.
Possible use cases are the following:

.. code-block:: python

    >>> from particle import Particle
    >>> from particle import Geant3ID, PythiaID
    >>>
    >>> g3id = Geant3ID(8)
    >>> p = Particle.from_pdgid(g3id.to_pdgid())
    >>>
    >>> p = Particle.find(pdgid=g3id.to_pdgid())
    >>> p.name
    'pi+'

    >>> pythiaid = PythiaID(211)
    >>> p = Particle.from_pdgid(pythiaid.to_pdgid())

    >>> p = Particle.find(pdgid=pythiaid.to_pdgid())
    >>> p.name
    'pi+'


Acknowledgements
----------------

Support for this work was provided by the National Science Foundation
cooperative agreement OAC-1450377 (DIANA/HEP) and OAC-1836650 (IRIS-HEP).
Any opinions, findings, conclusions or recommendations expressed in this material
are those of the authors and do not necessarily reflect the views of the National Science Foundation.


.. |Scikit-HEP| image:: https://scikit-hep.org/assets/images/Scikit--HEP-Project-blue.svg
   :target: https://scikit-hep.org

.. |PyPI version| image:: https://img.shields.io/pypi/v/particle.svg
   :target: https://pypi.python.org/pypi/particle

.. |Conda-forge version| image:: https://img.shields.io/conda/vn/conda-forge/particle.svg
   :target: https://anaconda.org/conda-forge/particle

.. |Zenodo DOI| image:: https://zenodo.org/badge/DOI/10.5281/zenodo.2552429.svg
   :target: https://doi.org/10.5281/zenodo.2552429

.. |GitHub Actions Status: CI| image:: https://github.com/scikit-hep/particle/workflows/CI/badge.svg
   :target: https://github.com/scikit-hep/particle/actions

.. |Code Coverage| image:: https://codecov.io/gh/scikit-hep/particle/graph/badge.svg?branch=master
   :target: https://codecov.io/gh/scikit-hep/particle?branch=master

.. |Code style: black| image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black

.. |Binder| image:: https://mybinder.org/badge_logo.svg
   :target: https://mybinder.org/v2/gh/scikit-hep/particle/master?urlpath=lab/tree/notebooks/ParticleDemo.ipynb
