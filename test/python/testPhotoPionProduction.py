import mpc
import pylab as lab
import sys
# make sure root is startet in Batch mode
sys.argv.append('-b')
import ROOT

def getSlope(interaction, energy, charge, count = 100000):
    c = mpc.Candidate()
    c.current.setId(mpc.getNucleusId(1, charge))
    c.current.setEnergy(energy)
    c.setCurrentStep(0.0 * mpc.Mpc)

    h = ROOT.TH1F('', '', 100, 0, 1000)

    for i in range(count):
        c.setNextStep(100000 * mpc.Mpc)
        c.clearInteractionStates()
    
        interaction.process(c)
        h.Fill(c.getNextStep() / mpc.Mpc)
    if h.GetEffectiveEntries() == 0:
        return [0, 0]
    f = ROOT.TF1('f1', 'expo')
    h.Fit(f, "q")
    
    s = -f.GetParameter(1)
    ds = f.GetParError(1) * s ** 2
    return [s, ds]
    
def compare(type, name, count = 100000):
    print "> compare ", name
    ppp = mpc.PhotoPionProduction(type)
    E, P, N = lab.genfromtxt(mpc.getDataPath('/PhotoPionProduction/' + name + '.txt'), unpack=True)

    p = lab.zeros(len(E))
    n = lab.zeros(len(E))
    print "[",
    for i in range(len(E)):
        print '=',
        sds = getSlope(ppp, E[i] * mpc.EeV, 1, count)
        p[i] = sds[0]
        sds = getSlope(ppp, E[i] * mpc.EeV, 0, count)
        n[i] = sds[0]
    print "]"
    lab.plot(E, p, 'k+', label="proton simulated", linewidth=2, markeredgewidth=2)
    lab.plot(E, P, "r", label="proton data")
    lab.plot(E, n, 'k.', label="neutron simulated")
    lab.plot(E, N, "b", label="neutron data")
    lab.xlabel('energy [EeV]')
    lab.ylabel('rate [1/Mpc]')
    lab.legend(loc='lower right')
    lab.grid()
    lab.semilogx()
    lab.savefig('PhotoPionProduction_' + name + '.png', bbox_inches='tight')
    lab.close()

compare(mpc.PhotoPionProduction.CMB, "cmb");
compare(mpc.PhotoPionProduction.CMBIR, "cmbir");
compare(mpc.PhotoPionProduction.IR, "ir", 1000000);