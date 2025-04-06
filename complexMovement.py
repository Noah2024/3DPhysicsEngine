from Definitions import *

def defaultScene():
    Floor = Entity(model="cube", scale=(100,1,100), visible = False, collider="box")
    Entity(model=Grid(width=10, height=10), scale=Vec3(100,100,100)).world_rotation_x += 90
    
    Floor = Entity(model="cube", scale=(100,1,100), visible = False, collider="box", rotation = Vec3(90,0,0), position=Vec3(0,50,50))
    Entity(model=Grid(width=10, height=10), scale=Vec3(100,100,100), position = Vec3(0,50,50))
    
    Floor = Entity(model="cube", scale=(100,1,100), visible = False, collider="box", rotation = Vec3(90,0,0), position=Vec3(0,50,-50))
    Entity(model=Grid(width=10, height=10), scale=Vec3(100,100,100), position = Vec3(0,50,-50))
    
    Floor = Entity(model="cube", scale=(100,1,100), visible = False, collider="box", rotation = Vec3(0, 0, 90), position=Vec3(50,50,0))
    Entity(model=Grid(width=10, height=10), scale=Vec3(100,100,100), position = Vec3(50,50,0)).world_rotation = Vec3(0, 90, 0)

    Floor = Entity(model="cube", scale=(100,1,100), visible = False, collider="box", rotation = Vec3(0, 0, 90), position=Vec3(-50,50,0))
    Entity(model=Grid(width=10, height=10), scale=Vec3(100,100,100), position = Vec3(-50,50,0)).world_rotation = Vec3(0, 90, 0)

    #Floor = Entity(model="cube", scale=(100,1,100), visible = False, collider="box", position=Vec3(0,100,0))
    #Entity(model=Grid(width=10, height=10), scale=Vec3(100,100,100), position=Vec3(0,100,0)).world_rotation_x += 90

var = spaceSetUp()
def setSceneObjs():                            #-2
        testObj = Object(var, velocity=Vec3(1,0,0), objTrack=True, gravity=True)
        testObj.position = Vec3(0, 98, 0)#4.9
        testObj.totalEnergy = Vec3(0,testObj.mass * abs(var.FGRAV) * testObj.position.y,0)

var.defaultScene = defaultScene
var.setSceneObjs = setSceneObjs

var.loadEngine()
var.EditorCamera.start_position = Vec3(0,50,0)

