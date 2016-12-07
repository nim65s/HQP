import robot_config as conf
from wrapper import Wrapper
from viewer_utils import Viewer
from tasks import *
from simulator import Simulator
from pinocchio.utils import zero as mat_zeros
import trajectories as traj
from solvers import NProjections
import os
import time
actual_path = os.path.dirname(os.path.abspath('HQP'))

#__ Config                                                                                                       
viewerName = 'Parkour'
robotName = "Skelette"
model_path = conf.model_path
#__ create the robot                                                                                             
robot = Wrapper(actual_path+model_path)
dt = conf.dt
q0 = conf.half_sitting
v0 = mat_zeros(robot.nv)
#__ Create simulator: robot + viewer                                                                             
simulator = Simulator('Sim1', q0.copy(), v0.copy(), 0.1, robotName, robot)
nq = simulator.robot.nq
nv = simulator.robot.nv
#simulator.viewer.updateRobotConfig(q0, robotName)                                                               

#__ Create Solver                                                                                                
solver =NProjections('Solv1', q0.copy(), v0.copy(), 0.1, robotName, robot)
#se3.computeJacobians(solver.robot.model, solver.robot.data, solver.)                                            

#__ Create Tasks                                                                                                 
''' KEEP FEET STATIC '''
# get desired state                                                                                              
idxRF = solver.robot.model.getFrameId('mtp_r')
idxLF = solver.robot.model.getFrameId('mtp_l')
oMrf = solver.robot.framePosition(idxRF)
oMlf = solver.robot.framePosition(idxLF)

# create trajectories                                                                                            
RFtraj = traj.ConstantSE3Trajectory('keepRF',oMrf)
LFtraj = traj.ConstantSE3Trajectory('keepLF',oMlf)

# create tasks                                                                                                   
RF = SE3Task(solver.robot, idxRF, RFtraj,'Keep Right Foot Task')
RF.kp = 1
RF.kv = 0.1
LF = SE3Task(solver.robot, idxLF, LFtraj, 'Keep Left Foot Task')
LF.kp = 1
LF.kv = 0.1

''' MOVE RIGHT HAND TO A TARGET '''
target= se3.SE3.Identity()
target.translation = np.matrix([.2,.4,.6]).T
robot.viewer.gui.addXYZaxis('world/target', [1., 1., 0., .5], 0.03, 0.3)
robot.placeObject('world/target', target, True)
# create trajectories                                                                                            
RHtraj = traj.ConstantSE3Trajectory('reachRH',target)

# create tasks                                                                                                   
idxRH = solver.robot.model.getFrameId('fingers_r')
RH = SE3Task(solver.robot, idxRH, RHtraj,'Reaching Task')
RH.adaptativeGain = True

#__ Stack the tasks                                                                                              
solver.addTask([RF, LF], [1,3])
solver.addTask(RH, 4)

#_Simulate                                                                                                       
t=0
dt = 0.1

# First order solution                                                                                           
for i in range(40):
    v = solver.inverseKinematics1st(t)
    simulator.increment(robot.q, v, dt, t)
    t += dt

time.sleep(1)
robot.display(q0)
time.sleep(1)


# Second order solution                                                                                          
t=0
for i in range(40):
    a = solver.inverseKinematics2nd(0)
    simulator.increment2(robot.q, a, dt, t)
    t += dt



