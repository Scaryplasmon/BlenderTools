import bpy
import bmesh
from mathutils import Vector

class ANNOTATION_OT_convert_to_mesh(bpy.types.Operator):
    bl_idname = "annotation.convert_to_mesh"
    bl_label = "Convert annotation to mesh"
    bl_description = "Convert the current Annotation layer into a mesh"

    def execute(self, context):
        # Get the Grease Pencil object and the active layer
        gp_object = context.scene.grease_pencil
        if not gp_object:
            self.report({'ERROR'}, 'No active Grease Pencil object')
            return {'CANCELLED'}

        annotations = gp_object.layers.active
        if not annotations:
            self.report({'ERROR'}, 'No active annotation layer')
            return {'CANCELLED'}

        # Create a new mesh object for output
        mesh_data = bpy.data.meshes.new('AnnotationMesh')
        mesh_object = bpy.data.objects.new('AnnotationMesh', mesh_data)

        # Link the newly created objects to the scene
        context.collection.objects.link(mesh_object)

        # Convert strokes to mesh
        bm = bmesh.new()
        mode_2d = context.scene.annotation2D
        smooth = context.scene.smooth
        verts = []
        offset = context.scene.Offset


        for stroke in annotations.frames[0].strokes:
            last_point = None
            for i, point in enumerate(stroke.points):
                loc = mesh_object.matrix_world.inverted() @ point.co
                
                # bm_vert = bm.verts.new(loc)
                # verts.append(bm_vert)
                
                # Connect vertices with edges

                if mode_2d:
                    loc_offset = loc + Vector((0, offset, 0)) if i % 2 == 0 else loc - Vector((0, offset, 0))
                    bm_vert = bm.verts.new(loc_offset)
                    verts.append(bm_vert)

                    if last_point is not None and len(verts) > 2:
                        bm.faces.new((last_point, bm_vert, verts[-3]))
                
                else:
                    bm_vert = bm.verts.new(loc)
                    
                    if last_point is not None:
                        bm.edges.new((last_point, bm_vert))

                last_point = bm_vert

        # Update the actual mesh from the BMesh data
        bm.to_mesh(mesh_data)
        bm.free()
        
        ## Merge based on the "Merge Distance" value
        bpy.context.view_layer.objects.active = mesh_object
        mesh_object.select_set(True)
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.remove_doubles(threshold=context.scene.MergeDistance)
        bpy.ops.mesh.normals_make_consistent(inside=False)
        bpy.ops.mesh.tris_convert_to_quads()
        bpy.ops.object.mode_set(mode='OBJECT')
        if smooth:
            bpy.ops.object.shade_smooth()
        else:
            bpy.ops.object.shade_flat()
            

        # Hide the annotation layer and make the created mesh active
        annotations.hide = not context.scene.annotation_visibility


        return {'FINISHED'}

class ANNOTATION_OT_remove_layer(bpy.types.Operator):
    bl_idname = "annotation.remove_layer"
    bl_label = "Delete Layer"
    bl_description = "Delete the active annotation layer"

    def execute(self, context):
        bpy.ops.gpencil.layer_annotation_remove()
        return {'FINISHED'}
    
def update_annotations_visibility(self, context):
    gp_object = context.scene.grease_pencil
    if not gp_object:
        return
      
    annotations = gp_object.layers.active
    if not annotations:
        return
    
    annotations.hide = not self.annotation_visibility

class ANNOTATION_PT_mesh_conversion(bpy.types.Panel):
    bl_label = "Annotation to Mesh"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Annotation to Mesh"

    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene, "MergeDistance")
        layout.operator("annotation.convert_to_mesh", text="Convert")
        # Add "Visibility" property
        layout.prop(context.scene, "annotation_visibility", text="Visibility")
        # Add "DeleteLayer" button
        layout.operator("annotation.remove_layer", icon='X', text="DeleteLayer")
        layout.prop(context.scene, 'annotation2D', text="2D")
        layout.prop(context.scene, 'smooth', text="Smooth")
        layout.prop(context.scene, "Offset", text="Offset")

def register():
    bpy.types.Scene.annotation_visibility = bpy.props.BoolProperty(update=update_annotations_visibility)
    bpy.utils.register_class(ANNOTATION_OT_remove_layer)
    bpy.utils.register_class(ANNOTATION_OT_convert_to_mesh)
    bpy.utils.register_class(ANNOTATION_PT_mesh_conversion)
    bpy.types.Scene.MergeDistance = bpy.props.FloatProperty(name="Merge Distance", default=0.001, precision=6)
    bpy.types.Scene.annotation2D = bpy.props.BoolProperty(name="2D", default=False)
    bpy.types.Scene.Offset = bpy.props.FloatProperty(name="Offset", default=0.1, precision=3)
    bpy.types.Scene.smooth = bpy.props.BoolProperty(name="Smooth", default=False)


def unregister():
    bpy.utils.unregister_class(ANNOTATION_OT_remove_layer)
    bpy.utils.unregister_class(ANNOTATION_PT_mesh_conversion)
    bpy.utils.unregister_class(ANNOTATION_OT_convert_to_mesh)
    del bpy.types.Scene.MergeDistance
    del bpy.types.Scene.annotation_visibility
    del bpy.types.Scene.annotation2D
    del bpy.types.Scene.smooth
    del bpy.types.Scene.Offset



if __name__ == "__main__":
    register()
