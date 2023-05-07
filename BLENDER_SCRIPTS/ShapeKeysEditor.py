import bpy
import random


class RandomizeXShapeKeysOperator(bpy.types.Operator):
    """Randomize shape keys starting with x"""
    bl_idname = "object.randomize_x_shape_keys"
    bl_label = "Randomize X Shape Keys"
    bl_options = {'REGISTER', 'UNDO'}
    
    x: bpy.props.StringProperty(name="x", default="")

    def execute(self, context):
        # Get the active object
        obj = context.active_object

        # Iterate through all the selected objects
        for obj in context.selected_objects:
            # Iterate through all the shape keys
            for key in obj.data.shape_keys.key_blocks:
                # Check if the shape key name starts with x
                if key.name.startswith(self.x):
                    # Assign a random value clamped between the slider's min and max values
                    random_value = random.uniform(key.slider_min, key.slider_max)
                    key.value = random_value
        return {'FINISHED'}
    
class ResetShapeKeysOperator(bpy.types.Operator):
    """Reset shape keys starting with n"""
    bl_idname = "object.reset_n_shape_keys"
    bl_label = "Reset N Shape Keys"
    bl_options = {'REGISTER', 'UNDO'}
    
    n: bpy.props.StringProperty(name="n", default="")

    def execute(self, context):
        # Get the active object
        obj = context.active_object

        # Iterate through all the selected objects
        for obj in context.selected_objects:
            # Iterate through all the shape keys
            for key in obj.data.shape_keys.key_blocks:
                # Check if the shape key name starts with x
                if key.name.startswith(self.n):
                    # Assign a random float value between 0 and 1
                    key.value = 0
        return {'FINISHED'}

class DeleteShapeKeysOperator(bpy.types.Operator):
    """Delete shape keys starting with delete"""
    bl_idname = "object.delete_shape_keys"
    bl_label = "Delete Shape Keys"
    bl_options = {'REGISTER', 'UNDO'}

    delete: bpy.props.StringProperty(name="delete", default="")

    def execute(self, context):
        # Iterate through all the selected objects
        for obj in context.selected_objects:
            # Iterate through all the shape keys
            for key in obj.data.shape_keys.key_blocks:
                # Check if the shape key name starts with delete
                if key.name.startswith(self.delete):
                    bpy.ops.object.mode_set(mode='EDIT')
                    bpy.ops.mesh.select_all(action='SELECT')
                    bpy.context.scene.tool_settings.use_uv_select_sync = False
                    bpy.ops.object.mode_set(mode='OBJECT')
                    obj.active_shape_key_index = obj.data.shape_keys.key_blocks.find(key.name)
                    # Remove the shape key
                    bpy.ops.object.shape_key_remove(all=False, apply_mix=False)

        return {'FINISHED'}

class TransferShapeKeysOperator(bpy.types.Operator):
    """Transfer shape keys starting with transfer"""
    bl_idname = "object.transfer_shape_keys"
    bl_label = "Transfer Shape Keys"
    bl_options = {'REGISTER', 'UNDO'}

    transfer: bpy.props.StringProperty(name="transfer", default="")

    def execute(self, context):
        # Get the active object
        active_obj = context.active_object

        # Ensure mesh has basis shape key
        if not active_obj.data.shape_keys:
            basis_key = active_obj.shape_key_add(name="Basis")

        # Iterate through all the selected objects except the active one
        for obj in [o for o in context.selected_objects if o != active_obj]:
            # Iterate through all the shape keys
            for key in obj.data.shape_keys.key_blocks:
                # Check if the shape key name starts with transfer
                if key.name.startswith(self.transfer):
                    # Transfer the shape key
                    transferred_key = active_obj.shape_key_add(name=key.name)
                    
                    # Copy the shape key data using insert() method
                    for vert_src, vert_dst in zip(key.data, transferred_key.data):
                        vert_dst.co = vert_src.co

        return {'FINISHED'}

class SetMinMaxShapeKeysOperator(bpy.types.Operator):
    """Set Min and Max value of all shape keys except for Basis"""
    bl_idname = "object.set_min_max_shape_keys"
    bl_label = "Set Min Max Shape Keys"
    bl_options = {'REGISTER', 'UNDO'}

    min_value: bpy.props.FloatProperty(name="Min", default=-1.0)
    max_value: bpy.props.FloatProperty(name="Max", default=1.0)

    def execute(self, context):
        # Iterate through all the selected objects
        for obj in context.selected_objects:
            if not obj.data.shape_keys:
                continue
            
            # Iterate through all the shape keys
            for key in obj.data.shape_keys.key_blocks:
                if key.name != "Basis":
                    key.slider_min = self.min_value
                    key.slider_max = self.max_value

        return {'FINISHED'}


class ShapeKeyPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Blend Shapes"
    bl_idname = "OBJECT_PT_shape_keys"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"

    def draw(self, context):
        layout = self.layout
        obj = context.object
        if obj and obj.type == 'MESH' and obj.data.shape_keys:
            shape_keys = obj.data.shape_keys
            
            row = layout.row()
            row.prop(context.scene, "x_value", text="x")
            row.operator("object.randomize_x_shape_keys", text="Randomize X").x=context.scene.x_value
            
            row = layout.row()
            row.prop(context.scene, "n_value", text="n")
            row.operator("object.reset_n_shape_keys", text="Reset N").n=context.scene.n_value

            row = layout.row()
            row.prop(context.scene, "delete_value", text="delete")
            row.operator("object.delete_shape_keys", text="delete Keys").delete=context.scene.delete_value
            
            row = layout.row()
            row.prop(context.scene, "transfer_value", text="Transfer")
            row.operator("object.transfer_shape_keys", text="Transfer Keys").transfer=context.scene.transfer_value

            row = layout.row()
            col = row.column(align=True)
            col.prop(context.scene, "min_value", text="Min")
            col.prop(context.scene, "max_value", text="Max")
            set_min_max_op = row.operator("object.set_min_max_shape_keys",
                                        text="Set Min Max")
            set_min_max_op.min_value = context.scene.min_value
            set_min_max_op.max_value = context.scene.max_value

def register():
    bpy.utils.register_class(ShapeKeyPanel)
    bpy.utils.register_class(RandomizeXShapeKeysOperator)
    bpy.utils.register_class(ResetShapeKeysOperator)
    bpy.utils.register_class(DeleteShapeKeysOperator)
    bpy.utils.register_class(TransferShapeKeysOperator)
    bpy.utils.register_class(SetMinMaxShapeKeysOperator)
    
    bpy.types.Scene.min_value = bpy.props.FloatProperty(name="Min",default=0.0)
                                                         
    bpy.types.Scene.max_value = bpy.props.FloatProperty(name="Max",default=1.0)
                                                            
    bpy.types.Scene.x_value = bpy.props.StringProperty(name="x", default="")
    bpy.types.Scene.n_value = bpy.props.StringProperty(name="n", default="")
    bpy.types.Scene.delete_value = bpy.props.StringProperty(name="delete", default="")
    bpy.types.Scene.transfer_value = bpy.props.StringProperty(name="transfer", default="")

def unregister():
    bpy.utils.unregister_class(ShapeKeyPanel)
    bpy.utils.unregister_class(RandomizeXShapeKeysOperator)
    bpy.utils.unregister_class(ResetShapeKeysOperator)
    bpy.utils.unregister_class(DeleteShapeKeysOperator)
    bpy.utils.unregister_class(TransferShapeKeysOperator)
    bpy.utils.unregister_class(SetMinMaxShapeKeysOperator)
    
    del bpy.types.Scene.min_value
    del bpy.types.Scene.max_value
    del bpy.types.Scene.x_value
    del bpy.types.Scene.n_value
    del bpy.types.Scene.delete_value
    del bpy.types.Scene.transfer_value

if __name__ == "__main__":
    register()