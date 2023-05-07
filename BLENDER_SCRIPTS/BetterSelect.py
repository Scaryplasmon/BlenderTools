import bpy
import bmesh
from bpy.props import FloatProperty
from mathutils import Vector


def select_faces_by_size(context, size_threshold):
    obj = context.active_object
    if obj.mode != 'EDIT':
        return

    mesh = bmesh.from_edit_mesh(obj.data)

    for face in mesh.faces:
        area = face.calc_area()
        # Select faces with area smaller than the size threshold
        if area < size_threshold:
            face.select_set(True)
        else:
            face.select_set(False)


    
    bmesh.update_edit_mesh(obj.data)


def select_elements_by_location(context, location):
    obj = context.active_object
    if obj.mode != 'EDIT':
        return

    mesh = bmesh.from_edit_mesh(obj.data)
    cursor = context.scene.cursor.location

    # Select Vertices
    for vert in mesh.verts:
        local_vert_co = obj.matrix_world.inverted() @ vert.co
        select_vert = False
        if (location == 'TOP' and local_vert_co.z > cursor.z) or \
           (location == 'BOTTOM' and local_vert_co.z < cursor.z) or \
           (location == 'LEFT' and local_vert_co.x < cursor.x) or \
           (location == 'RIGHT' and local_vert_co.x > cursor.x) or \
           (location == 'FRONT' and local_vert_co.y > cursor.y) or \
           (location == 'BACK' and local_vert_co.y < cursor.y):
            select_vert = True

        if select_vert:
            vert.select_set(True)

    # Select Edges
    for edge in mesh.edges:
        midpoint = (edge.verts[0].co + edge.verts[1].co) / 2
        local_edge_midpoint = obj.matrix_world.inverted() @ midpoint
        select_edge = False
        if (location == 'TOP' and local_edge_midpoint.z > cursor.z) or \
           (location == 'BOTTOM' and local_edge_midpoint.z < cursor.z) or \
           (location == 'LEFT' and local_edge_midpoint.x < cursor.x) or \
           (location == 'RIGHT' and local_edge_midpoint.x > cursor.x) or \
           (location == 'FRONT' and local_edge_midpoint.y > cursor.y) or \
           (location == 'BACK' and local_edge_midpoint.y < cursor.y):
            select_edge = True

        if select_edge:
            edge.select_set(True)

    # Select Faces
    for face in mesh.faces:
        local_face_center = obj.matrix_world.inverted() @ face.calc_center_median()
        select_face = False
        if (location == 'TOP' and local_face_center.z > cursor.z) or \
           (location == 'BOTTOM' and local_face_center.z < cursor.z) or \
           (location == 'LEFT' and local_face_center.x < cursor.x) or \
           (location == 'RIGHT' and local_face_center.x > cursor.x) or \
           (location == 'FRONT' and local_face_center.y > cursor.y) or \
           (location == 'BACK' and local_face_center.y < cursor.y):
            select_face = True

        if select_face:
            face.select_set(True)

    bmesh.update_edit_mesh(obj.data)


class SelectElementsByLocationOperator(bpy.types.Operator):
    bl_idname = "object.select_element_by_location"
    bl_label = "Select Elements by Location"

    location : bpy.props.StringProperty()

    def execute(self, context):
        select_elements_by_location(context, self.location)
        return {'FINISHED'}

class SelectFacesBySizeOperator(bpy.types.Operator):
    bl_idname = "object.select_faces_by_size"
    bl_label = "Select Faces by Size Threshold"

    size_threshold : bpy.props.FloatProperty()

    def execute(self, context):
        select_faces_by_size(context, self.size_threshold)
        return {'FINISHED'}



class VertSelectionByCursor(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Vert Selection"
    bl_label = "Vertices by Cursor"

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.operator(SelectElementsByLocationOperator.bl_idname, icon='TRIA_UP', text="").location = 'TOP'
        row.operator(SelectElementsByLocationOperator.bl_idname, icon='TRIA_DOWN', text="").location = 'BOTTOM'

        row = layout.row()
        row.operator(SelectElementsByLocationOperator.bl_idname, icon='TRIA_LEFT', text="").location = 'LEFT'
        row.operator(SelectElementsByLocationOperator.bl_idname, icon='TRIA_RIGHT', text="").location = 'RIGHT'

        row = layout.row()
        row.operator(SelectElementsByLocationOperator.bl_idname, icon='BACK', text="").location ='FRONT'
        row.operator(SelectElementsByLocationOperator.bl_idname, icon='PLUS', text="").location ='BACK'

        layout.separator()

        col = layout.column(align=True)
        col.prop(context.scene, 'size_threshold', text="Size Threshold")
        # Set the size_threshold property of the operator
        op = col.operator(SelectFacesBySizeOperator.bl_idname, text="Select faces < Size Threshold")
        op.size_threshold = bpy.context.scene.size_threshold

def register():
    bpy.utils.register_class(SelectElementsByLocationOperator)
    bpy.utils.register_class(SelectFacesBySizeOperator)
    bpy.utils.register_class(VertSelectionByCursor)
    setattr(bpy.types.Scene, 'size_threshold', FloatProperty(name= "Face Size Threshold", default= 0.05))

def unregister():
    bpy.utils.unregister_class(SelectElementsByLocationOperator)
    bpy.utils.unregister_class(SelectFacesBySizeOperator)
    bpy.utils.unregister_class(VertSelectionByCursor)
    delattr(bpy.types.Scene, 'size_threshold', FloatProperty(name= "Face Size Threshold", default= 0.05))
    

if __name__ == "__main__":
    register()
