from mpc import *
from pylab import *


E = 10 # proton energy [EeV]
nT = 500 # number of trajectories
nS = 50 # number of sampling points to simulate
nP = range(30) # sampling points for plot

# create turbulent field with B_RMS = 1 nG and 0.5 Mpc correlation length
vGrid = VectorGrid(Vector3d(0, 0, 0), 128, 0.05 * Mpc)
initTurbulence(vGrid, 1 * nG, 0.1 * Mpc, 2.2 * Mpc, -11/3.)
propa = DeflectionCK(MagneticFieldGrid(vGrid))

Lc = turbulentCorrelationLength(0.1 * Mpc, 2.2 * Mpc, -11/3.) / Mpc
Brms = 1 # nG
Rg = 1.08 * E / Brms # Mpc

age = linspace(1, 150, nS)
distance, rms1, rms2 = zeros((3, nS))

for j in range(nT):
	if j % (nT // 10) == 0:
		print j

	ps = ParticleState()
	ps.setId(nucleusId(1, 1))
	ps.setEnergy(E * EeV)	
	ps.setDirection(Random.instance().randUnitVectorOnSphere())
	ps.setPosition(Vector3d(0, 0, 0))
	c = Candidate(ps)

	for i in range(nS):
		maxLen = MaximumTrajectoryLength(age[i] * Mpc)
		c.setNextStep(c.getNextStep() * 0.99)
		c.setActive(True)

		while c.isActive():
			propa.process(c)
			maxLen.process(c)

		x = c.current.getPosition() / Mpc
		p = c.current.getDirection()
		p0 = c.initial.getDirection()
		distance[i] += x.getMag()
		rms1[i] += (x.getAngleTo(p))**2
		rms2[i] += (p0.getAngleTo(p))**2


distance /= nT
rms1 = (rms1 / nT)**.5
rms2 = (rms2 / nT)**.5

theory = 38 * (distance * Lc)**.5 * Brms / E * pi/180

figure()
plot(distance[nP], rms1[nP], label='position, final direction')
plot(distance[nP], theory[nP] / 3**.5, 'k--')
plot(distance[nP], rms2[nP], label='initial, final direction')
plot(distance[nP], theory[nP], 'k--', label='Harari et al.')
xlabel('Distance [Mpc]')
ylabel('RMS(Deflection) [rad]')
legend(loc='lower right', frameon=False)
s = 'Gyroradius $r_g=%.2f$ Mpc\nCorr. Length $L_c=%.2f$ Mpc'%(Rg, Lc)
text(0.05, 0.95, s, ha='left', va='top', transform=gca().transAxes)
savefig('TurbulentDeflection.png', bbox_inches='tight')

show()

