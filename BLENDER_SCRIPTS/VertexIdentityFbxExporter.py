import bpy
import os
def export_fbx(filepath):
    bpy.ops.export_scene.fbx(
        filepath=filepath,
        check_existing=True,
        use_selection=True,
        global_scale=1.0,
        object_types={'MESH','ARMATURE','EMPTY'},
        use_mesh_modifiers=False,
        use_mesh_modifiers_render=False,
        mesh_smooth_type='OFF',
        add_leaf_bones=False,
        bake_anim=False
    )
# Set your output directory here (use double backslashes)
output_directory = 'C:\\Users\\andre\\Desktop'
# Ensure the output directory exists
os.makedirs(output_directory, exist_ok=True)

allowed_object_types = {'MESH', 'ARMATURE', 'EMPTY'}

# Iterate through all objects and export individual FBX files
for obj in bpy.context.scene.objects:
    if obj.type in allowed_object_types:
        # Select only the current object
        #bpy.ops.object.select_all(action='DESELECT')
        #obj.select_set(True)
        # Set output file name
        output_file = os.path.join(output_directory, f"{obj.name}.fbx")
        # Export selected object as FBX
        export_fbx(output_file)