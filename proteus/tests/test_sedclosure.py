from proteus import Comm, Profiling
import numpy as np
import numpy.testing as npt
import unittest

comm = Comm.init()
Profiling.procID = comm.rank()

Profiling.logEvent("Testing SedClosure")


class TestHsu(unittest.TestCase):
    def testGradularDrag1(self):
        from proteus.mprans.SedClosure import HsuSedStress
        # Constant params
        C4e = 1.
        C3e = 1.2
        aDarcy = 1.
        bForch = 1.
        grain = 0.1
        packFraction = 0.2
        packMargin = 0.01
        uf = np.array([5.,4.],"d")
        us = np.array([1.,1.],"d") 
        umag_temp = (uf - us)*(uf - us)
        umag = np.sqrt(sum(umag_temp))
        sigmaC = 1.1
        # Testing for sedF >> packFraction
        nu = 1.
        sedF = 0.5
        drag = aDarcy * nu* sedF /((1.-sedF)*grain**2) +  bForch * umag / grain
        sedSt = HsuSedStress( aDarcy, bForch, grain, packFraction, packMargin, sigmaC, C3e, C4e)
        # For sedF > pacFraction - > drag = a * nu* sedF /((1-sedF)*grain^2) + beta * umag / grain
        drag2 = sedSt.betaCoeff(sedF, uf, us, nu)

        self.assertTrue(drag == drag2)
    def testGradularDrag2(self):
        from proteus.mprans.SedClosure import HsuSedStress
        C4e = 1.
        C3e = 1.2
        sigmaC = 1.1
        aDarcy = 1.
        bForch = 1.
        grain = 0.1
        packFraction = 0.2
        packMargin = 0.01
        uf = np.array([5.,4.],"d")
        us = np.array([1.,1.],"d") 
        umag_temp = (uf - us)*(uf - us)
        umag = np.sqrt(sum(umag_temp))
        # Testing for sedF << packFraction and Rep = (1. - sed) * umag*nu/grain = 0.9 * 5. * 0.1 / 1. = 0.45
        nu = 1.
        sedF = 0.1
        Rep = (1.- sedF)*umag*grain / nu    
        drag =  ( 24. * (1.+0.15*Rep**(0.687))/Rep) * 0.75 * umag * (1. -sedF)**(-1.65) / grain # Chen and Hsu 2014
        sedSt = HsuSedStress(aDarcy, bForch, grain, packFraction, packMargin, sigmaC, C3e, C4e)
        drag2 = sedSt.betaCoeff(sedF, uf, us, nu)
        self.assertTrue(round(drag,10) == round(drag2,10))

    def testGradularDrag3(self):
        from proteus.mprans.SedClosure import HsuSedStress
        # Constant params
        C4e = 1.
        C3e = 1.2
        aDarcy = 1.
        sigmaC = 1.1
        bForch = 1.
        grain = 0.1
        packFraction = 0.2
        packMargin = 0.01
        uf = np.array([5.,4.],"d")
        us = np.array([1.,1.],"d") 
        umag_temp = (uf - us)*(uf - us)
        umag = np.sqrt(sum(umag_temp))
        # Testing for sedF << packFraction and Rep > 1000
        sedF = 0.1
        nu = 1e-4
        Rep = (1.- sedF) * umag * grain / nu    
        drag =  ( 0.44 * 0.75 * umag * (1. -sedF)**(-1.65) )/ grain # Chen and Hsu 2014
        sedSt = HsuSedStress( aDarcy, bForch, grain, packFraction, packMargin, sigmaC, C3e, C4e)
        drag2 = sedSt.betaCoeff(sedF, uf, us, nu)
        self.assertTrue(round(drag,10) == round(drag2,10))
    def testGradularDrag4(self):
        from proteus.mprans.SedClosure import HsuSedStress
        # Constant params
        C4e = 1.
        C3e = 1.2
        sigmaC = 1.1
        aDarcy = 1.
        bForch = 1.
        grain = 0.1
        packFraction = 0.2
        packMargin = 0.01
        uf = np.array([5.,4.],"d")
        us = np.array([1.,1.],"d") 
        umag_temp = (uf - us)*(uf - us)
        umag = np.sqrt(sum(umag_temp))
        # Testing for sedF =  packFraction +0.5 packmargin and Rep > 1000
        sedF = 0.205
        nu = 1e-4
        Rep = (1.- sedF) * umag * grain / nu
        draga = aDarcy * nu* sedF /((1.-sedF)*grain**2) +  bForch * umag / grain
    
        dragb =  ( 0.44 * 0.75 * umag * (1. -sedF)**(-1.65) )/ grain # Chen and Hsu 2014
        w = 0.5 + (sedF - packFraction) / (2. * packMargin)
        drag = w*draga + (1.-w) * dragb
        sedSt = HsuSedStress( aDarcy, bForch, grain, packFraction, packMargin, sigmaC, C3e, C4e)
        drag2 = sedSt.betaCoeff(sedF, uf, us, nu)
        self.assertTrue(round(drag,10) == round(drag2,10))
    def testgs0(self):
        from proteus.mprans.SedClosure import HsuSedStress
        C4e = 1.
        C3e = 1.2
        sigmaC = 1.1
        aDarcy = 1.
        bForch = 1.
        grain = 0.1
        packFraction = 0.2
        packMargin = 0.01
        f = 8
        sedSt = HsuSedStress( aDarcy, bForch, grain, packFraction, packMargin, sigmaC, C3e, C4e)
        sedF = 0.2
        gs0 = sedSt.gs0(sedF)
        self.assertTrue(gs0 == 0.5*(2-sedF)/(1-sedF)**3)
        sedF = 0.55
        gs0 = sedSt.gs0(sedF)
        self.assertTrue(round(gs0,f) ==round( 0.5*(2-0.49)/(1-0.49)**3 * (0.64-0.49)/(0.64-sedF),f))
        sedF = 0.65
        gs0 = sedSt.gs0(sedF)
        self.assertTrue(round(gs0,f) == round(0.5*(2-0.49)/(1-0.49)**3 * (0.64-0.49)/(0.64-0.635),f))
    def testTkeSed(self):
        from proteus.mprans.SedClosure import HsuSedStress
        import random
        C4e = 1.
        C3e = 1.2
        sigmaC = 1.1
        aDarcy = 1.
        bForch = 1.
        grain = 0.1
        packFraction = 0.2
        packMargin = 0.01
        f = 10
        uf = np.array([5.,4.],"d")
        us = np.array([1.,1.],"d") 
        gradC=np.array([0.1,0.1])
        rhoS = 2000
        rhoF = 1000
        nu = 1e-4
        nuT = 1e-2
        sedSt = HsuSedStress( aDarcy, bForch, grain, packFraction, packMargin, sigmaC, C3e, C4e)
        sedF = 0.3
# Setting 0 t_c
        theta_n = random.random() + 1e-30
        kappa_n = random.random() + 1e-30
        epsilon_n = random.random() + 1e-30


        beta = sedSt.betaCoeff(sedF, uf, us, nu)      
        t_p =rhoS/ beta
        l_c = np.sqrt(np.pi)*grain / (24.*sedF * sedSt.gs0(sedF))
        t_cl = min(l_c/np.sqrt(theta_n),0.165*kappa_n/epsilon_n)
        aa = 1/( 1. + t_p/t_cl)

       
        es1 = 2.*beta * rhoS*(1-aa)*sedF*kappa_n/((1-sedF)*rhoF)

        UgradC = np.dot((uf - us),gradC)

        es2  = beta * rhoF * nuT * UgradC / ((1-sedF)*rhoF)

        kappa_sed = sedSt.kappa_sed(sedF,rhoF,rhoS,uf,us,gradC,nu,theta_n,kappa_n,epsilon_n,nuT)
        self.assertTrue(round(kappa_sed,f) ==round( -es1+es2,f))
        
    def testEpsSed(self):
        from proteus.mprans.SedClosure import HsuSedStress
        import random
        C4e = 1.
        C3e = 1.2
        sigmaC = 1.1
        aDarcy = 1.
        bForch = 1.
        grain = 0.1
        packFraction = 0.2
        packMargin = 0.01
        f = 8
        uf = np.array([5.,4.],"d")
        us = np.array([1.,1.],"d") 
        gradC=np.array([0.1,0.1])
        rhoS = 2000
        rhoF = 1000
        nu = 1e-4
        nuT = 1e-2
        sedSt = HsuSedStress( aDarcy, bForch, grain, packFraction, packMargin, sigmaC, C3e, C4e)
        sedF = 0.3
# Setting 0 t_c
        theta_n = random.random() + 1e-30
        kappa_n = random.random() + 1e-30
        epsilon_n = random.random() + 1e-30


        beta = sedSt.betaCoeff(sedF, uf, us, nu)      
        t_p =rhoS/ beta
        l_c = np.sqrt(np.pi)*grain / (24.*sedF * sedSt.gs0(sedF))
        t_cl = min(l_c/np.sqrt(theta_n),0.165*kappa_n/epsilon_n)
        aa = 1/( 1. + t_p/t_cl)

       
        es1 = 2.*beta * rhoS*(1-aa)*sedF*kappa_n/((1-sedF)*rhoF)

        UgradC = np.dot((uf - us),gradC)

        es2  = beta * rhoF * nuT * UgradC / ((1-sedF)*rhoF)

        eps_sed = sedSt.eps_sed(sedF,rhoF,rhoS,uf,us,gradC,nu,theta_n,kappa_n,epsilon_n,nuT)

        self.assertTrue(round(eps_sed,f) ==round( -C3e*es1*epsilon_n/kappa_n+C4e*es2*epsilon_n/kappa_n,f))

    def testMint(self):
        from proteus.mprans.SedClosure import HsuSedStress
        sigmaC = 1.1
        C4e = 1.
        C3e = 1.2
        aDarcy = 1.
        bForch = 1.
        grain = 0.1
        packFraction = 0.2
        packMargin = 0.01
        uf = np.array([5.,4.],"d")
        us = np.array([1.,1.],"d") 
        gradc = np.array([0.1,0.1],"d") 
        sedF = 0.205
        nu = 1e-4
        nuT = 1e-2
        sedSt = HsuSedStress( aDarcy, bForch, grain, packFraction, packMargin, sigmaC, C3e, C4e)
        beta = sedSt.betaCoeff(sedF, uf, us, nu)      
        mint = sedSt.mInt(sedF, uf, us, uf, us , nu, nuT, gradc)
        self.assertTrue(round(mint.all(),10) == round((-sedF*beta*(uf-us) - sedF * beta * gradc * nuT / sigmaC).all() , 10))
    def testdMintdUf(self):
        from proteus.mprans.SedClosure import HsuSedStress
        sigmaC = 1.1
        C4e = 1.
        C3e = 1.2
        aDarcy = 1.
        bForch = 1.
        grain = 0.1
        packFraction = 0.2
        packMargin = 0.01
        uf = np.array([5.,4.],"d")
        us = np.array([1.,1.],"d") 
        gradc = np.array([0.1,0.1],"d") 
        sedF = 0.205
        nu = 1e-4
        nuT = 1e-2
        sedSt = HsuSedStress( aDarcy, bForch, grain, packFraction, packMargin, sigmaC, C3e, C4e)
        beta = sedSt.betaCoeff(sedF, uf, us, nu)      
        mint = sedSt.dmInt_duFluid(sedF, uf, us , nu)
        self.assertTrue(round(mint,10) == round(  - sedF*beta , 10))
    def testdMintdUs(self):
        from proteus.mprans.SedClosure import HsuSedStress
        C4e = 1.
        C3e = 1.2
        sigmaC = 1.1
        aDarcy = 1.
        bForch = 1.
        grain = 0.1
        packFraction = 0.2
        packMargin = 0.01
        uf = np.array([5.,4.],"d")
        us = np.array([1.,1.],"d") 
        gradc = np.array([0.1,0.1],"d") 
        sedF = 0.205
        nu = 1e-4
        nuT = 1e-2
        sedSt = HsuSedStress( aDarcy, bForch, grain, packFraction, packMargin, sigmaC, C3e, C4e)
        beta = sedSt.betaCoeff(sedF, uf, us, nu)      
        mint = sedSt.dmInt_duSolid(sedF, uf, us , nu)
        self.assertTrue(round(mint,10) == round(  sedF*beta , 10))



if __name__ == '__main__':
    unittest.main(verbosity=2)