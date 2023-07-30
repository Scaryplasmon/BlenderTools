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
        mode_3d = context.scene.annotation3D
        smooth = context.scene.smooth
        verts = []
        offsetX = context.scene.OffsetX
        offsetY = context.scene.OffsetY
        offsetZ = context.scene.OffsetZ
        thickness = context.scene.thickness

        # Generate perpendicular vectors
        x_offset = (offsetX * Vector((1, 0, 0)))
        y_offset = (offsetY * Vector((0, 1, 0)))
        z_offset = (offsetZ * Vector((0, 0, 1)))


        for stroke in annotations.frames[0].strokes:
            last_point = None
            last_verts = None
            for i, point in enumerate(stroke.points):
                loc = mesh_object.matrix_world.inverted() @ point.co
                bm_vert = None

                if mode_2d:
                    loc_offset = loc + Vector((offsetX, offsetY, offsetZ)) if i % 2 == 0 else loc - Vector((offsetX, offsetY, offsetZ))
                    bm_vert = bm.verts.new(loc_offset)
                    verts.append(bm_vert)

                    if last_point is not None and len(verts) > 2:
                        bm.faces.new((last_point, bm_vert, verts[-3]))
                    last_point = bm_vert
                        
                elif mode_3d:
                    offsets = [x_offset, y_offset, -1 * x_offset, -1 * y_offset]

                    new_bm_verts = [bm.verts.new(loc + offset) for offset in offsets]

                    if last_verts is not None:
                        for i, (prev_bm_vert, bm_vert) in enumerate(zip(last_verts, new_bm_verts)):
                            edge = bm.edges.new((prev_bm_vert, bm_vert))
                            if i > 0:
                                bm.faces.new((last_verts[i - 1], last_verts[i], new_bm_verts[i], new_bm_verts[i - 1]))
                    
                    last_verts = new_bm_verts


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

        if mode_3d:
            # Close the gaps between surfaces using looptools_bridge
            new_edges = [e for e in mesh_data.edges if e.select]
            groups = [[], []]
            while new_edges:
                start_edge = new_edges.pop()
                groups[0].append(start_edge)
                current_edge = start_edge
                current_verts = list(current_edge.vertices)

                while True:
                    next_edge = None
                    for search_edge in new_edges:
                        search_verts = list(search_edge.vertices)
                        if set(current_verts) & set(search_verts):
                            next_edge = search_edge
                            break
                    
                    if next_edge is not None:
                        new_edges.remove(next_edge)
                        groups[1 if len(groups[0]) % 2 == 0 else 0].append(next_edge)
                        current_edge = next_edge
                        current_verts = list(current_edge.vertices)
                    else:
                        break

            for group in groups:
                for edge in group:
                    mesh_data.edges[edge.index].select_set(True)
                bpy.ops.mesh.looptools_bridge(loft=False)

                for edge in group:
                    mesh_data.edges[edge.index].select_set(False)
        else:
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.remove_doubles(threshold=context.scene.MergeDistance)

        bpy.ops.mesh.normals_make_consistent(inside=False)

        if mode_3d:
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
            bpy.ops.mesh.select_all(action='DESELECT')
        
            edges_group_1 = [(e.verts[0].index, e.verts[1].index) for e in mesh_data.edges if e.is_boundary][:2]
            edges_group_2 = [(e.verts[0].index, e.verts[1].index) for e in mesh_data.edges if e.is_boundary][2:]
        
            for eg in [edges_group_1, edges_group_2]:
                for v1, v2 in eg:
                    mesh_data.vertices[v1].select = True
                    mesh_data.vertices[v2].select = True
                    mesh_data.edges[mesh_data.edges.get((v1, v2))].select_set(True)
        
                bpy.ops.mesh.looptools_bridge(loft=False)
                
            bpy.ops.mesh.select_all(action='SELECT')
        
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
        layout.prop(context.scene, 'annotation3D', text="3D")
        layout.prop(context.scene, 'smooth', text="Smooth")
        layout.prop(context.scene, "OffsetX", text="OffsetX")
        layout.prop(context.scene, "OffsetY", text="OffsetY")
        layout.prop(context.scene, "OffsetZ", text="OffsetZ")
        layout.prop(context.scene, "thickness", text="Thickness")
        

def register():
    bpy.types.Scene.thickness = bpy.props.FloatProperty(name="Thickness", default=0.1, precision=3)
    bpy.types.Scene.annotation_visibility = bpy.props.BoolProperty(update=update_annotations_visibility)
    bpy.utils.register_class(ANNOTATION_OT_remove_layer)
    bpy.utils.register_class(ANNOTATION_OT_convert_to_mesh)
    bpy.utils.register_class(ANNOTATION_PT_mesh_conversion)
    bpy.types.Scene.MergeDistance = bpy.props.FloatProperty(name="Merge Distance", default=0.001, precision=6)
    bpy.types.Scene.annotation2D = bpy.props.BoolProperty(name="2D", default=False)
    bpy.types.Scene.annotation3D = bpy.props.BoolProperty(name="3D", default=False)
    bpy.types.Scene.OffsetX = bpy.props.FloatProperty(name="OffsetX", default=0.1, precision=3)
    bpy.types.Scene.OffsetY = bpy.props.FloatProperty(name="OffsetY", default=0.1, precision=3)
    bpy.types.Scene.OffsetZ = bpy.props.FloatProperty(name="OffsetZ", default=0.1, precision=3)
    bpy.types.Scene.smooth = bpy.props.BoolProperty(name="Smooth", default=False)


def unregister():
    bpy.utils.unregister_class(ANNOTATION_OT_remove_layer)
    bpy.utils.unregister_class(ANNOTATION_PT_mesh_conversion)
    bpy.utils.unregister_class(ANNOTATION_OT_convert_to_mesh)
    del bpy.types.Scene.annotation3D
    del bpy.types.Scene.MergeDistance
    del bpy.types.Scene.annotation_visibility
    del bpy.types.Scene.annotation2D
    del bpy.types.Scene.smooth
    del bpy.types.Scene.OffsetX
    del bpy.types.Scene.OffsetY
    del bpy.types.Scene.OffsetZ
    del bpy.types.Scene.thickness


if __name__ == "__main__":
    register()

