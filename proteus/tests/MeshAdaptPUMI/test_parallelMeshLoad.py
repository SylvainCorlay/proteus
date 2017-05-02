from ctypes import *
from proteus import MeshTools
from proteus import cmeshTools
from proteus import Domain
from proteus.MeshAdaptPUMI import MeshAdaptPUMI
from proteus import Comm
from nose.tools import eq_ as eq
from nose.tools import ok_ as ok
import os
from petsc4py import PETSc
import pytest

@pytest.mark.skip(reason="need to run in parallel")
def test_parallelLoadPUMI(verbose=0):
    """Test to load parallel PUMI model and mesh"""
    comm = Comm.init()
    eq(comm.size(),2)
    testDir=os.path.dirname(os.path.abspath(__file__))
    domain = Domain.PUMIDomain()
    Model=testDir+ '/Prism.dmg'
    Mesh=testDir + '/Prism.smb'
    domain.PUMIMesh=MeshAdaptPUMI.MeshAdaptPUMI()
    domain.PUMIMesh.loadModelAndMesh(Model, Mesh)
    mesh = MeshTools.TetrahedralMesh()
    mesh.cmesh = cmeshTools.CMesh()
    mesh.convertFromPUMI(domain.PUMIMesh, domain.faceList, domain.regList,parallel = comm.size() > 1, dim = domain.nd)
    eq(mesh.nElements_global,8148)
    eq(mesh.nNodes_global,1880)
    eq(mesh.nEdges_global,11001)
    eq(mesh.nElementBoundaries_global,17270)
    #Ideally, we can assert whether each rank gets the proper number of mesh entities/
    #With the present setup, that information doesn't seem accessible
    #if(comm.rank()==0):
    #    eq(mesh.nElements_owned,4074)
    #    eq(mesh.nNodes_owned,994)
    #    eq(mesh.nEdges_owned,8729)
    #    eq(mesh.nElementBoundaries_owned,5648)

if __name__ == '__main__':
    import nose
    nose.main(defaultTest='test_meshLoad:test_parallelLoadPUMI')


