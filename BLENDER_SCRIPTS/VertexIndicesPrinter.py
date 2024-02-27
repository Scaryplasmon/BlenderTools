import bpy
import bmesh
import json

def export_vertex_data_json():
    vertex_data = []

    if bpy.context.active_object.mode == 'EDIT':
        mesh_data = bpy.context.active_object.data
        bm = bmesh.from_edit_mesh(mesh_data)

        for v in bm.verts:
            if v.select:
                vertex_data.append({
                    "index": v.index,
                    "position": [v.co.x, v.co.y, v.co.z]
                })

        bm.free()
    else:
        print("The active object is not in Edit mode")
        return

    with open("vertex_data.json", "w") as file:
        json.dump(vertex_data, file)

export_vertex_data_json()
