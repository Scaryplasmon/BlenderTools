import bpy
import os
import math
import time

# Paths
gltf_file_path = "C:\\Users\\andre\\Downloads\\mushroom_lowpoly\\scene.gltf"  # Replace with your glTF file path
output_folder = "C:\\Users\\andre\\Downloads\\mushroom_lowpoly\\textures" # Replace with your desired output path

# Clear existing objects
bpy.ops.wm.read_factory_settings(use_empty=True)

# Import glTF
bpy.ops.import_scene.gltf(filepath=gltf_file_path)

# Create camera
cam_data = bpy.data.cameras.new("Camera")
cam_ob = bpy.data.objects.new("Camera", cam_data)
bpy.context.scene.collection.objects.link(cam_ob)

cam_ob.location = (0, -5, 0)
cam_ob.rotation_euler = (math.radians(90), 0, 0)

# Ensure there's a world in the scene
if not bpy.context.scene.world:
    bpy.context.scene.world = bpy.data.worlds.new(name="New World")

# Set the world background to a neutral gray
bpy.context.scene.world.color = (0.7, 0.8, 0.1)


bpy.context.scene.camera = cam_ob

sun_data = bpy.data.lights.new(name="Sun", type='SUN')
sun_object = bpy.data.objects.new(name="Sun", object_data=sun_data)
bpy.context.collection.objects.link(sun_object)

# Position sun lamp
sun_object.location = (0, 0, 10)  # Above the scene
sun_object.rotation_euler = (math.radians(30), 0, 0) # 30 degrees in radians on the X-axis

# Set render settings
bpy.context.scene.render.image_settings.file_format = 'JPEG'
bpy.context.scene.render.filepath = output_folder
bpy.context.scene.render.resolution_x = 512
bpy.context.scene.render.resolution_y = 512
bpy.context.scene.render.resolution_percentage = 100

# Set render settings to use Workbench
bpy.context.scene.render.engine = 'BLENDER_WORKBENCH'

# Workbench specific settings
bpy.context.scene.display.shading.light = 'STUDIO'
bpy.context.scene.display.shading.color_type = 'MATERIAL'

start_time = time.time()
# Render frames
for frame in range(300):
    bpy.context.scene.frame_set(frame)
    bpy.context.scene.render.filepath = os.path.join(output_folder, f"frame_{frame:04}.jpeg")
    bpy.ops.render.render(write_still=True)

end_time = time.time()

total_render_time = end_time - start_time
print(f"Total Render Time: {total_render_time:.1f} seconds")