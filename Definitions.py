from ursina import *
from ursina.shaders import lit_with_shadows_shader
from ursina.prefabs.first_person_controller import FirstPersonController
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import math
import time

var = None
class spaceSetUp():#Needs to be made variable
    def __init__(Self, **kwargs):
        Self.FGRAV = kwargs.get("gravity",-9.8)#m/s^2
        Self.ZERO = Vec3(0,0,0)
        Self.simulating = False
        Self.firstPerson = True
        Self.startTime = 0
        Self.simSpeed = 1.0
        Self.SIMFPS =   100 #"MAX" to use systems max fps (will cause variable dT)"MAX" #
        Self.lastUpdate = 0.0#Used for updatingFrames on fixed FPS timescale
        Self.activeObjs = []
        Self.simChangeAttempt = 0
        Self.simChangeDebounce = 5
        Self.objectTracking = None
        Self.objInfo = {"Force": [], "Acceleration":[], "Velocity":[], "Potential Energy":[], "Kenetic Energy":[], "Momentum":[] }
        Self.timeStamps = []
        Self.simTime = 0
        Self.concTime = 0
        Self.timeLostToCalc = 0.0
        Self.totalFPS = 0
        Self.totalFrames = 0
        Self.singleFrame = False
        global var
        var = Self
        
    def cameraSetUp(Self):
        Self.EditorCamera = EditorCamera(enabled = False, position = Vec3(0,0,0), move_speed=0)#removed
        Self.FPC = FirstPersonController(gravity = 0, speed = 0, grounded = False, enabled=True)
    
    def uiSetUp(Self):
        Self.uiNotification = Text(text="Simulation Paused", x=-.2, y=.5, visible=True, scale=2)
        Self.uiSimTime = Text(text="SimTime: 0.0", x=-.85, y=.5, visible=True, scale=1.75)
        Self.uiSimSpeed = Text(text="SimSpeed: 1.0x", x=.4, y=.5, visible=True, scale=2)
        Self.uiSimFps = Text(text="Sim FPS: ",  x=-.85, y=-.4, visible=True, scale=2)

    def defaultScene(Self):
        Entity(model=Grid(width=10, height=10), scale=Vec3(100,100,100)).world_rotation_x += 90
        Entity(model="arrow", scale=(10,10,10), alpah=74, color = color.rgb(153, 255, 204)).world_rotation_z += -90#.world_rotation_y+=90
        Entity(model="arrow", scale=(10,10,10), alpah=74, color=color.rgb(255, 153, 153)).world_rotation_x += -90#.world_rotation_y+=90
        Entity(model="arrow", scale=(10,10,10), alpah=74, color=color.rgb(102, 255, 255)).world_rotation_y += 90#.world_rotation_y+=90
        Wall = Entity(model="cube", scale=(5,5,10), color=color.blue, position=Vec3(40,2.5,0), alpha=84, collider="box")
        Floor = Entity(model="cube", scale=(100,1,100), texture="radial_gradient", color=color.blue, collider="box")

    def setSceneObjs(Self):
        testObj = Object(Self, velocity=Vec3(2,0,-2), objTrack=True)
        testObj.position = Vec3(0, 98, 0)#4.9
        testObj.totalEnergy = Vec3(0,testObj.mass * abs(var.FGRAV) * testObj.position.y,0)
    #var.objectTracking = testObj

    def resetSceneObjs(Self):
        for I in Self.activeObjs:
            destroy(I, delay=0.0)
        Self.setSceneObjs()

    def setSceneInd(Self):
        Self.activeObjs = []
        Self.simTime = 0
        Self.simSpeed = 1.0
        Self.timeStamps = []
        print(f"Active Objecets: {len(var.activeObjs)}")

    def loadEngine(Self):#Needs to be made varaible
        app = Ursina(borderless = False, development_mode=True)
        Self.cameraSetUp()
        Self.uiSetUp()
        Self.defaultScene()
        Self.setSceneInd()
        Self.setSceneObjs()
        app.run()

#var = spaceSetUp()#AKA var
#materialsList = {"default": [], "nonObj":[]}

def vecMag(Vec):
    return(sqrt(Vec.x**2+Vec.y**2+Vec.z**2))

def absVec3(Vec):
    return Vec3(abs(Vec.x), abs(Vec.y), abs(Vec.z))

def reflectVector(v, n): #ChatGPT Generated - Still understnading 
    n = n.normalized()
    scalar = v.dot(n) * 2
    return v - n * scalar

def phantomObj(realObj):
    savedPos = Vec3(realObj.position.x, realObj.position.y, realObj.position.z)
    return Entity(model="sphere", color=color.green, position=savedPos, visible=True, enabled=True, scale = realObj.scale)
    print(f"Phantom Object Created At: {realObj.position}")

def startSimulation():
     print("simulation started")
     var.startTime = 0
     var.timeStamps = []
     var.simulating = True
     var.uiNotification.text = "Simulaiton Running"
     var.startTime = time.perf_counter()
     if var.objectTracking != None:
        var.objInfo = {"Force": [], "Acceleration":[], "Velocity":[], "Gravitational Potential Energy":[], "Kenetic Energy":[], "Total Energy":[]}
        
def genMatPlotLib():
    timeAsNumpy = np.asarray(var.timeStamps)
    index = 1
    if var.objectTracking != None:
        fig = plt.figure(num=None, figsize=(22, 10), dpi=80, facecolor='w', edgecolor='k')
        fig.title = "Breakdown of Object's motion"
        for key in var.objInfo:
            axe = fig.add_subplot(2,3,index)
            axe.title.set_text(key)
            axe.plot(timeAsNumpy, np.asarray(var.objInfo[key]))
            index += 1
        title = "Targeted Object"
        plt.show()

def pauseSimulation():
    print("simulation pasued")
    var.simulating = False
    var.uiNotification.text = "Simulation Paused"
    endTime = time.perf_counter()
    elapsedTime = endTime - var.startTime
    var.concTime += elapsedTime
    print("elpasedTime", elapsedTime)
    print("This time will be off from its sim time counter part if FPS is fixed")
    print(f"Average FPS: {var.totalFPS / var.totalFrames}")
    if var.objectTracking != False: genMatPlotLib()
    

def increaseSimSpeed():
    limit = 10.0
    inc = .1
    if (var.simSpeed + inc) <= limit:
        var.simSpeed += inc
    else:
        simSpeed = 10.0
    var.uiSimSpeed.text = f"SimSpeed: {round(var.simSpeed, 2)}x"
    

def decreaseSimSpeed():
    limit = -1
    inc = .1
    if (var.simSpeed - inc) >= limit:
        var.simSpeed -= inc
    else:
        var.simSpeed = -1
    var.uiSimSpeed.text = f"SimSpeed: {round(var.simSpeed, 2)}x"

def updateVec3(Vec1, Vec2):
    newVec3 = Vec3(Vec1.x+Vec2.x, Vec1.y+Vec2.y, Vec1.z+Vec2.z)
    return(newVec3)

def Vec3To4(Vec3):
    return Vec4(Vec3.x, Vec3.y, Vec3.z, 0)
    
class Object(Entity):
    def __init__(Self,var,**kwargs):
        Self.var = var
        super().__init__(model=kwargs.get("model", "sphere"),
        scale=kwargs.get("scale", Vec3(1,1,1)),
        shader=lit_with_shadows_shader,
        collider=kwargs.get("model", "sphere")),
        Self.position = kwargs.get("position", Vec3(0,98,0))
        Self.uniqueName = kwargs.get("uniqueName", "TestBall")
        Self.immovable = kwargs.get("immovable", False)
        Self.gravityOn = kwargs.get("gravity", True)
        Self.mass = kwargs.get("mass", 1)
        Self.momentum = kwargs.get("momentum", Vec3(0,0,0))  #kgm/s^2
        Self.acceleration = kwargs.get("acceleration", Vec3(0,0,0)) #m/s^2
        Self.velocity = kwargs.get("velocity", Vec3(0,0,0)) #m/s
        Self.keneticEnergy = kwargs.get("keneticEnergy", Vec3(0,0,0))
        Self.netForce = kwargs.get("netForce", Vec3(0,0,0))
        Self.componentForces = kwargs.get("componentForces", [Vec3(0,0,0)])
        Self.objTrack = kwargs.get("objTrack", False)
        Self.collisionDebounce = .1
        Self.lastKnownCollision = 0.0
        #print(Self.velocity.normalized())
        Self.PotEnergy = Self.position.y*var.FGRAV*Self.mass*-1 if var.FGRAV != 0 and Self.gravityOn == True else 0
        # print(Self.PotEnergy)
        Self.keneticEnergy = vecMag(Self.velocity* Self.velocity * Self.velocity.normalized() *  Self.mass * .5)
        # print(Self.keneticEnergy)
        Self.totalEnergy = Self.PotEnergy + Self.keneticEnergy
        #Self.energyAggregate = 
        
        
        Self.material = "N/A"
        Self.density = "N/A"
        Self.volume = 1 #m^3
        #Self.angularVelocity = 0#1
        #Self.angularAcceleration = 0#1
        # print("Energy: ", Self.totalEnergy)
        #Self.totalWorkDone
        if Self.objTrack == True:
            var.objectTracking = Self
        var.activeObjs.append(Self)
            
    def applyForce(Self, other, force):
            Self.componentForces.append(force)
            if other != None: #only used for gravity and immovable objects
                other.componenetForces.append(force * -1) #Force is applied in the opposite direction to the other object
    def updateState(Self, dT):
        if len(Self.componentForces) != 0:
            for comp in Self.componentForces:
                Self.netForce += comp

        dX = Self.position - Self.lKP#dX is the change in position
        dV = dX/dT#dV is the change in velocity
                
        Self.lKP = Self.position#lastKnownPosition
        Self.impulse = Self.netForce * dT#AKA: dM (Change in momentum)|| F=dM/dT
        Self.momentum += Self.impulse#Self.mass * Self.velocity
        Self.acceleration = Self.impulse/(dT*Self.mass)#((Self.netForce)/Self.mass) #
        Self.velocity += Self.acceleration*dT#/instantFPS#  Self.momentum/Self.mass#
        #print(Self.velocity)
        Self.position += Self.velocity*dT#*var.simSpeed#/instantFPS

        #Self.dW = Self.netForce * (Self.velocity*dT)
        Self.keneticEnergy = 0.5 * Self.mass * (Self.velocity.x**2 + Self.velocity.y**2 + Self.velocity.z**2)#(Self.momentum*Self.momentum)/(2*Self.mass)#Self.dW#
        #work per dT # * Self.velocity *Self.acceleration *dT
        #Self.keneticEnergy += Self.dW #.5 * Self.mass * (Self.velocity * Self.velocity) #Self.totalEnergy-Self.PotEnergy#
        Self.PotEnergy = Self.position.y * var.FGRAV * Self.mass * -1#Need to account for gravity turing off#Vec3(0,Self.mass * abs(var.FGRAV) * Self.position.y,0)#Cause negative is just direction, not magnitude
        #print("Components: ", Self.PotEnergy, Self.keneticEnergy)
        #print("Total Diff: ", Self.totalEnergy)#-960.4000000000001
        # print(type(Self.keneticEnergy), type(Self.PotEnergy))
        Self.totalEnergy = Self.PotEnergy + Self.keneticEnergy
        print("Total Energy: ", Self.totalEnergy)
        # print(Self.keneticEnergy + Self.PotEnergy)
        # print(Self.keneticEnergy + Self.PotEnergy)
        if var.objectTracking != None and var.objectTracking == Self:
            obj = Self
            objInfo = var.objInfo
            var.timeStamps.append(var.simTime)
            force = Vec3(obj.netForce.x, obj.netForce.y, obj.netForce.z)
            objInfo["Force"].append(Vec3To4(force))
            accel = Vec3(obj.acceleration.x, obj.acceleration.y, obj.acceleration.z)
            objInfo["Acceleration"].append(Vec3To4(accel))
            vel = Vec3(obj.velocity.x, obj.velocity.y, obj.velocity.z)
            objInfo["Velocity"].append(Vec3To4(vel))
            objInfo["Gravitational Potential Energy"].append(obj.PotEnergy)
            #ken = Vec3(obj.keneticEnergy.x, obj.keneticEnergy.y, obj.keneticEnergy.z)
            objInfo["Kenetic Energy"].append(obj.keneticEnergy)
            objInfo["Total Energy"].append(Self.totalEnergy)#
            #objInfo["Position"].append(obj.position.y)

        Self.netForce = Vec3(0,0,0)
        Self.componentForces = []

def add_tag_to_entity(entity, text, y_offset=1.5, color=color.white, scale=2):#Chat GPT
    """Attach a floating text tag above any Ursina entity."""
    tag = Text(
        text=text,
        parent=entity,
        y=y_offset,
        z=-0.1,  # Slightly in front to avoid z-fighting
        scale=scale,
        origin=(0,0),
        color=color,
        background=True
    )
    return tag  # So you can keep a reference if you want to remove/update it later

def shiftVec(Vec):
    return Vec3(Vec.z, Vec.x, Vec.y)
def updateFPC(pos, speed):
    var.FPC.world_x += pos.x*speed
    var.FPC.world_y += pos.y*speed
    var.FPC.world_z += pos.z*speed
simChangeDebounce = 5
simChangeAttempt = 0
def update():
    if var.simulating == True:
        dT = time.dt if var.SIMFPS == "MAX" else 1/var.SIMFPS#dT is the ideal time betwen frames
        betwenFrames = time.time() - var.lastUpdate if var.SIMFPS != "MAX" else dT#betweenFrames is the actual time between frames
        dT = dT*var.simSpeed #dT is used for calculation to provide more consistnet data, betweenFrames is used to measure actual FPS
        if (betwenFrames*var.simSpeed >= dT):#MAX however will provide the fastest framerate the computer will allow 
            var.simTime += dT                                       #Which is why it uses time.dt, and will provide more inconsistent data
            instantFPS = 1/betwenFrames#dT
            var.uiSimTime.text = f"SimTime: {var.simTime}"
            var.uiSimFps.text = f"Sim FPS: {instantFPS}"#"Sim Fps Counter Disabled"#
            var.totalFPS += instantFPS#instantFPS
            var.totalFrames += 1
            for obj in var.activeObjs:
                # print(obj)
                if obj.gravityOn: obj.applyForce(None, Vec3(0,var.FGRAV*obj.mass,0))
                # Entity(model="sphere", color=color.white, scale=(1,1,1), position = obj.position, alpha=(54))#Phantom object
                obj.updateState(dT)
                rayVecMag = absVec3((obj.position - obj.lKP))+absVec3(obj.scale)#dP
                rayVecMag = sqrt(rayVecMag.x**2 + rayVecMag.y**2 + rayVecMag.z**2)
                rayVecDir = obj.velocity
                hitInfo = raycast(origin=obj.lKP, direction=rayVecDir, distance=rayVecMag, traverse_target=scene, ignore=list([obj]), debug=True)
                onDebounce = var.simTime - obj.lastKnownCollision < obj.collisionDebounce    

                if hitInfo.hit and not onDebounce:#If the raycast hit something and the last collision was more than obj.collisionDebounce seconds ago
                    
                    # obj.position = hitInfo.world_point
                    normal = hitInfo.world_normal
                    normal = Vec3(round_to_closest(normal.x, 1), round_to_closest(normal.y, 1), round_to_closest(normal.z, 1))#Will need to change later
                    hitMarker = Entity(model="sphere",world_position=hitInfo.world_point, scale=(1,1,1), alpah=74, color = color.orange)#.world_rotation_y+=90
                    add_tag_to_entity(hitMarker, f"Hit at: {var.simTime}", y_offset=1.5, color=color.red, scale=10)
                    print("--------obj Hit--------")
                    print(f"Normal: {normal}")
                    
                    for hit in hitInfo.entities:
                        print("Normal comp: ", normal.x, normal.y, normal.z)
                        print("Vel Before: ", obj.velocity)
                        print("Position: Before", obj.position)
                        print("Time of collision: ", var.simTime)
                        if type(hit) == Object:#True is only for objects which can be moved
                            restitution = 1.0  # 1.0 = perfectly elastic, <1.0 = loses energy
                            reflectedVelocity = reflectVector(obj.velocity, normal) * restitution
                            impulse = (reflectedVelocity - obj.velocity) * obj.mass#
                            obj.applyForce(hit, impulse / dT)  # Apply the force to both objects 
                            print("Is Object")
                        else:


                            #This was part of an expiermnt into a small conceptual issue with collisions, I haven't seen any practial issues so far, so im not going to continue to develop it
                            #Cuase presently it adds just a little bit of energy to the object, where as it shouldn't be, im being lazy and not fixing it, and using the other method until I actuall
                            #Run into an issue with it
                            # residualDistance = rayVecMag - vecMag(absVec3(obj.world_position - hit.world_position))#This is to account for the fact that an object can collid with an object before actually hitting it
                            # residualPosition = residualDistance * normal #Thus its position is slighly off from where it is supposed to be (This is a product of imprefect collisions and a fininate time step)
                            # obj.position = residualPosition
                            # print("Energy Before: ", obj.totalEnergy)
                            # energyAfterResidualPosition = abs(obj.totalEnergy) -  abs(Vec3(0, obj.position.y*var.FGRAV*obj.mass,0).y) #* restitution
                            # residualVelocity = normal * sqrt(2 * energyAfterResidualPosition / obj.mass) #This is to account for the fact that an object can collid with an object before actually hitting it
                            # impulse = (residualVelocity - obj.velocity) * obj.mass
                            restitution = 1.0  # 1.0 = perfectly elastic, <1.0 = loses energy

                            reflectedVelocity = reflectVector(obj.velocity, normal) * restitution
                            impulse = (reflectedVelocity - obj.velocity) * obj.mass#

                            obj.applyForce(None, impulse / dT)  # Apply the impulse as a force over the time step

                            #pauseSimulation()
                        #pauseSimulation()
                        
                    print("-----------------------")
                    obj.updateState(dT)#I don't know why this has to be here, but it does
                    print("Position: After", obj.position)
                    print("Vel After: ", obj.velocity)
                    obj.lastKnownCollision = var.simTime              
            if var.singleFrame == True:#Must have intital normal start
                var.simulating = False
                var.singleFrame = False
            var.lastUpdate = time.time()
            
    if var.firstPerson:
        #["w": var.FPC.forward, "s": var.FPC.back, "a":var.FPC.left, "d": var.FPC.right,
        #"e": var.FPC.up, "spacebar": var.FPC.up, "q": var.FPC.down]
        if held_keys["w"]:
            updateFPC(var.FPC.forward, 2)
        if held_keys["s"]:
            updateFPC(var.FPC.back, 2)
        if held_keys["a"]:
           updateFPC(var.FPC.left, 2)
        if held_keys["d"]:
            updateFPC(var.FPC.right, 2)
        if held_keys["e"] or held_keys["spacebar"]:
           updateFPC(var.FPC.up, 2)
        if held_keys["q"]:
            updateFPC(var.FPC.down, 2)
            
    if var.simChangeAttempt >= var.simChangeDebounce:
        if held_keys["up arrow"]:
            increaseSimSpeed()
        if held_keys["down arrow"]:
            decreaseSimSpeed()
        var.simChangeAttempt = 0
    else:
        var.simChangeAttempt += 1

def input(key):
    if key == "enter":
        if var.simulating:
            pauseSimulation()
        else:
            startSimulation()
    if key == "scroll up":
        pass
    if key == "scroll down":
        pass
    if key == "f up":
        if var.firstPerson:
            var.firstPerson = False
            var.FPC.enabled = False
            var.EditorCamera.enabled = True
        else:
            var.firstPerson = True
            var.EditorCamera.enabled = False
            var.FPC.enabled = True
    if not var.simulating:
        if key == "r":
            var.resetSceneObjs()
            var.setSceneInd()
            var.uiSimTime.text = f"SimTime: {var.simTime}"
            var.uiSimSpeed.text = f"SimSeed: {var.simSpeed}"
        if key == "right arrow up":#Must have inital normal start
            var.singleFrame = True
            var.simulating = True
        if key == "c" and var.FPC.enabled==True and var.objectTracking != False:
            var.FPC.look_at(var.objectTracking.position)
            
#app.run()
#To do list
#Make physics cals impulse and momnetum based
#Fix Kenetic Energy and Potential Energy
#Test collision with movable objects
#Add torque and angular momentum 
#Add air resistence and air density (Will need to calculate drag and lift for certian objects)
#Integrate materials and material properties (density, friction coefficents, etc.)
#Make a spring object
#Model collisions
