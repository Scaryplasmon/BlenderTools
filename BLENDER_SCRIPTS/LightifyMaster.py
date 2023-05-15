import bpy

view_layer = bpy.context.view_layer
objects = bpy.data.objects
active_object = bpy.context.active_object

def create_spot_rig():
    # Create new light datablock.
    light_data = bpy.data.lights.new(name="TrackTo_SPOT", type='SPOT')
    # Create new Empty
    emptylight = bpy.context.scene.objects.get('EMPTYLIGHT')

    # Check if already in the scene
    if emptylight:
        print ("AlreadyHere")    
    else :
        bpy.ops.object.empty_add(type='CUBE', radius=0.6, align='CURSOR', scale=(1, 1, 1))
        bpy.context.active_object.name = 'EMPTYLIGHT'
        
    #create new Light object

    light_object = bpy.data.objects.new(name='TrackTo_SPOT', object_data=light_data)

    #select new Light object

    view_layer.active_layer_collection.collection.objects.link(light_object)

    view_layer.objects.active = light_object

    #Set Data

    light_data.energy = 100

    #calculate distance //

    driver = light_data.driver_add('spot_size').driver

    var = driver.variables.new()

    var.type = 'TRANSFORMS'
    var.name = "spot_size"
    # variables have one or two targets 
    target = var.targets[0]
    target.id = bpy.data.objects.get('EMPTYLIGHT')

    target.transform_type = 'SCALE_AVG'
    target.transform_space = 'WORLD_SPACE'

    var2 = driver.variables.new()

    var2.type = 'LOC_DIFF'
    var2.name = "distance"

    # variables have one or two targets 
    target1 = var2.targets[0]
    target2 = var2.targets[1]

    target1.id = bpy.data.objects.get('EMPTYLIGHT')
    target2.id = bpy.context.active_object

    target1.transform_space = 'WORLD_SPACE'
    target2.transform_space = 'WORLD_SPACE'

    driver.expression = '(spot_size * distance) * 1.878 / (3.14)'


    #Constraint TrackTO
    light_object.constraints.new('TRACK_TO')
    light_object.constraints['Track To'].target = bpy.data.objects['EMPTYLIGHT']


def create_roof_rig():
    x = bpy.context.scene.cursor.location.x
    y = bpy.context.scene.cursor.location.y
    z = bpy.context.scene.cursor.location.z
    # Create new EmptyCenter//
    emptysphere = bpy.context.scene.objects.get('EMPTYSPHERE')
    # Check if already in the scene//
    if emptysphere:
        print ("AlreadyHere")    
    else :
        bpy.ops.object.empty_add(type='SPHERE', radius=0.8, align='CURSOR', scale=(1, 1, 1))
        bpy.context.active_object.name = 'EMPTYSPHERE'
        
    # Create new EmptyRoof//
    emptyroof = bpy.context.scene.objects.get('EMPTYROOF')

    # Check if already in the scene//
    if emptyroof:
        print ("AlreadyHere")    
    else :
        roof = bpy.ops.object.empty_add(type='CUBE', radius=1, align='CURSOR', scale=(3, 3, 0.5))
        bpy.context.active_object.name = 'EMPTYROOF'
        bpy.context.active_object.scale = (3, 3, 0.5)
        bpy.context.active_object.location = (0, 0, 2)

    # Create new arrowFront//
    arrowFront = bpy.ops.object.empty_add(type='SINGLE_ARROW', radius=1, scale=(1, 1, 1))
    bpy.context.active_object.name = 'ARROWFRONT'

    arrowBack = bpy.ops.object.empty_add(type='SINGLE_ARROW', radius=1, scale=(1, 1, 1))
    bpy.context.active_object.name = 'ARROWBACK'

    arrowLeft = bpy.ops.object.empty_add(type='SINGLE_ARROW', radius=1, scale=(1, 1, 1))
    bpy.context.active_object.name = 'ARROWLEFT'

    arrowRight = bpy.ops.object.empty_add(type='SINGLE_ARROW', radius=1, scale=(1, 1, 1))
    bpy.context.active_object.name = 'ARROWRIGHT'


    #AreaFront//
    bpy.ops.object.light_add(type='AREA', radius=1, align='WORLD', location=(x, y+1.5, z-1))
    bpy.context.active_object.name = 'AreaFront'
    Front = bpy.data.objects['AreaFront'].data
    Front.name = 'AreaFront'

    driver_front = Front.driver_add('energy').driver

    var_front = driver_front.variables.new()

    var_front.type = 'TRANSFORMS'
    var_front.name = "energy_front"

    target = var_front.targets[0]
    target.id = bpy.data.objects.get('ARROWFRONT')

    target.transform_type = 'SCALE_AVG'
    target.transform_space = 'WORLD_SPACE'

    var_front2 = driver_front.variables.new()

    var_front2.type = 'LOC_DIFF'
    var_front2.name = "distance"


    target1 = var_front2.targets[0]
    target2 = var_front2.targets[1]

    target1.id = bpy.data.objects.get('EMPTYSPHERE')
    target2.id = bpy.context.active_object

    target1.transform_space = 'WORLD_SPACE'
    target2.transform_space = 'WORLD_SPACE'

    driver_front.expression = '(energy_front  * 1000) / distance'

    rf = bpy.data.objects['EMPTYSPHERE'].rotation_euler[0]
    gf = bpy.data.objects['EMPTYSPHERE'].rotation_euler[1]
    bf = bpy.data.objects['EMPTYSPHERE'].rotation_euler[2]



    print (rf, gf, bf) 


    #ConstraintFRONT//
    bpy.context.active_object.constraints.new('FLOOR')
    bpy.context.active_object.constraints['Floor'].target = bpy.data.objects['EMPTYSPHERE']


    bpy.context.active_object.constraints.new('TRACK_TO')
    bpy.context.active_object.constraints['Track To'].target = bpy.data.objects['EMPTYSPHERE']


    #AreaBack//
    bpy.ops.object.light_add(type='AREA', radius=1, align='WORLD', location=(x, y-1.5, z-1))
    bpy.context.active_object.name = 'AreaBack'
    Back = bpy.data.objects['AreaBack'].data
    Back.name = 'AreaBack'

    driver_back = Back.driver_add('energy').driver

    var_back = driver_back.variables.new()

    var_back.type = 'TRANSFORMS'
    var_back.name = "energy_back"

    target = var_back.targets[0]
    target.id = bpy.data.objects.get('ARROWBACK')

    target.transform_type = 'SCALE_AVG'
    target.transform_space = 'WORLD_SPACE'

    var_front2 = driver_back.variables.new()

    var_front2.type = 'LOC_DIFF'
    var_front2.name = "distance"

    
    target1 = var_front2.targets[0]
    target2 = var_front2.targets[1]

    target1.id = bpy.data.objects.get('EMPTYSPHERE')
    target2.id = bpy.context.active_object

    target1.transform_space = 'WORLD_SPACE'
    target2.transform_space = 'WORLD_SPACE'

    driver_back.expression = '(energy_back  * 100) / distance'

    #ConstraintBACK//
    bpy.context.active_object.constraints.new('FLOOR')
    bpy.context.active_object.constraints['Floor'].target = bpy.data.objects['EMPTYSPHERE']


    bpy.context.active_object.constraints.new('TRACK_TO')
    bpy.context.active_object.constraints['Track To'].target = bpy.data.objects['EMPTYSPHERE']

    #AreaLeft//
    bpy.ops.object.light_add(type='AREA', radius=1, align='WORLD', location=(x+1.5, y, z-1))
    bpy.context.active_object.name = 'AreaLeft'
    Left = bpy.data.objects['AreaLeft'].data
    Left.name = 'AreaLeft'

    driver_left = Left.driver_add('energy').driver

    var_left = driver_left.variables.new()

    var_left.type = 'TRANSFORMS'
    var_left.name = "energy_left"
    
    target = var_left.targets[0]
    target.id = bpy.data.objects.get('ARROWLEFT')

    target.transform_type = 'SCALE_AVG'
    target.transform_space = 'WORLD_SPACE'

    var_front2 = driver_left.variables.new()

    var_front2.type = 'LOC_DIFF'
    var_front2.name = "distance"


    target1 = var_front2.targets[0]
    target2 = var_front2.targets[1]

    target1.id = bpy.data.objects.get('EMPTYSPHERE')
    target2.id = bpy.context.active_object

    target1.transform_space = 'WORLD_SPACE'
    target2.transform_space = 'WORLD_SPACE'

    driver_left.expression = '(energy_left  * 50) / distance'

    #ConstraintLEFT//
    bpy.context.active_object.constraints.new('FLOOR')
    bpy.context.active_object.constraints['Floor'].target = bpy.data.objects['EMPTYSPHERE']

    bpy.context.active_object.constraints.new('TRACK_TO')
    bpy.context.active_object.constraints['Track To'].target = bpy.data.objects['EMPTYSPHERE']

    #AreaRight//
    bpy.ops.object.light_add(type='AREA', radius=1, align='WORLD', location=(x-1.5, y, z-1))
    bpy.context.active_object.name = 'AreaRight'
    Right = bpy.data.objects['AreaRight'].data
    Right.name = 'AreaRight'

    driver_right = Right.driver_add('energy').driver

    var_right = driver_right.variables.new()

    var_right.type = 'TRANSFORMS'
    var_right.name = "energy_right"
    # variables have one or two targets 
    target = var_right.targets[0]
    target.id = bpy.data.objects.get('ARROWRIGHT')

    target.transform_type = 'SCALE_AVG'
    target.transform_space = 'WORLD_SPACE'

    var_front2 = driver_right.variables.new()

    var_front2.type = 'LOC_DIFF'
    var_front2.name = "distance"


    target1 = var_front2.targets[0]
    target2 = var_front2.targets[1]

    target1.id = bpy.data.objects.get('EMPTYSPHERE')
    target2.id = bpy.context.active_object

    target1.transform_space = 'WORLD_SPACE'
    target2.transform_space = 'WORLD_SPACE'

    driver_right.expression = '(energy_right  * 10) / distance'

    #ConstraintRIGHT//
    bpy.context.active_object.constraints.new('FLOOR')
    bpy.context.active_object.constraints['Floor'].target = bpy.data.objects['EMPTYSPHERE']

    bpy.context.active_object.constraints.new('TRACK_TO')
    bpy.context.active_object.constraints['Track To'].target = bpy.data.objects['EMPTYSPHERE']


    #Areas//
    af = bpy.data.objects.get('AreaFront')
    ab = bpy.data.objects.get('AreaBack')
    al = bpy.data.objects.get('AreaLeft')
    ar = bpy.data.objects.get('AreaRight')

    #Arrows//
    ef = objects['ARROWFRONT']
    eb = objects['ARROWBACK']
    el = objects['ARROWLEFT']
    er = objects['ARROWRIGHT']

    if af and ef:
        ef.parent = af

    if ab and eb:
        eb.parent = ab

    if al and el:
        el.parent = al

    if ar and er:
        er.parent = ar


    ER = objects['EMPTYROOF']

    ar.parent = ER
    af.parent = ER
    al.parent = ER
    ab.parent = ER




class SpotRig(bpy.types.Operator):
    bl_idname = 'spot.create'
    bl_label = 'Lightify.spot'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        create_spot_rig()
        return {'FINISHED'}
    
class RoofRig(bpy.types.Operator):
    bl_idname = 'roof.create'
    bl_label = 'Lightify.roof'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        create_roof_rig()
        return {'FINISHED'}

class LightifyPanel(bpy.types.Panel):
    bl_label = 'Lightify'
    bl_idname = 'OBJECT_PT_lightify'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Lightify'

    def draw(self, context):
        layout = self.layout
        layout.operator('spot.create', text='Create Spot Rig')
        layout.operator('roof.create', text='Create Roof Rig')

def register():
    bpy.utils.register_class(SpotRig)
    bpy.utils.register_class(RoofRig)
    bpy.utils.register_class(LightifyPanel)

def unregister():
    bpy.utils.unregister_class(SpotRig)
    bpy.utils.unregister_class(RoofRig)
    bpy.utils.unregister_class(LightifyPanel)

if __name__ == '__main__':
    register()
