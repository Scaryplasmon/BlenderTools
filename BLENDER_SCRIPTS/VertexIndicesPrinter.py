import bpy
import bmesh

def print_selected_vertex_indices():
    # Check if context is in Edit mode
    if bpy.context.active_object.mode == 'EDIT':
        # Get the mesh data and create a temporary BMesh object to manipulate
        mesh_data = bpy.context.active_object.data
        bm = bmesh.from_edit_mesh(mesh_data)

        # Collect the indices of selected vertices
        selected_vertex_indices = [v.index for v in bm.verts if v.select]

        # Print selected vertex indices in numerical order
        print(sorted(selected_vertex_indices))

        # Cleanup (not strictly necessary, but good practice)
        bm.free()
    else:
        print("The active object is not in Edit mode")

# Call the function
print_selected_vertex_indices()
