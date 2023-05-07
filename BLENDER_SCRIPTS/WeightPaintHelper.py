import bpy

# Set blend mode to MIX operator
class SetMixBlendModeOperator(bpy.types.Operator):
    bl_idname = "object.set_mix_blend_mode"
    bl_label = "Mix"
    
    def execute(self, context):
        # Get the brush named "Draw"
        brush = bpy.data.brushes['Draw']
        
        # Set the blend mode to MIX
        brush.blend = 'MIX'
        
        return {'FINISHED'}

# Set blend mode to SUBTRACT operator
class SetSubtractBlendModeOperator(bpy.types.Operator):
    bl_idname = "object.set_subtract_blend_mode"
    bl_label = "Subtract"
    
    def execute(self, context):
        # Get the brush named "Draw"
        brush = bpy.data.brushes['Draw']
        
        # Set the blend mode to SUBTRACT
        brush.blend = 'SUB'
        
        return {'FINISHED'}
        
# Create a panel for the buttons
class BlendModePanel(bpy.types.Panel):
    bl_label = "Blend Mode"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tool'

    @classmethod
    def poll(cls, context):
        return context.mode == 'PAINT_WEIGHT'

    def draw(self, context):
        layout = self.layout
        
        row = layout.row()
        row.operator("object.set_mix_blend_mode")
        
        row = layout.row()
        row.operator("object.set_subtract_blend_mode")

def register():
    bpy.utils.register_class(BlendModePanel)
    bpy.utils.register_class(SetMixBlendModeOperator)
    bpy.utils.register_class(SetSubtractBlendModeOperator)

def unregister():
    bpy.utils.unregister_class(BlendModePanel)
    bpy.utils.unregister_class(SetMixBlendModeOperator)
    bpy.utils.unregister_class(SetSubtractBlendModeOperator)

if __name__ == "__main__":
    register()
