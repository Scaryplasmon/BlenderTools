import bpy


class SimplifyAnimationPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_simplify"
    bl_label = "Simplify Animation"
    bl_space_type = 'DOPESHEET_EDITOR'
    bl_region_type = 'UI'

    def draw(self, context):
        layout = self.layout

        ks = context.scene.keying_sets_all
        layout.prop_search(context.scene, "active_keying_set", ks, "rna_type.name")
        
        row = layout.row()
        row.prop(context.scene, 'step', text='Step Size')
        
        row = layout.row()
        row.operator("object.simplify_animation")
        row.operator("object.simplify_object_animation")


class SimplifyAnimationOperator(bpy.types.Operator):
    bl_idname = "object.simplify_animation"
    bl_label = "Simplify"

    def execute(self, context):
        remove_inbetween(context, bpy.context.selected_pose_bones)
        return {'FINISHED'}


class SimplifyObjectAnimationOperator(bpy.types.Operator):
    bl_idname = "object.simplify_object_animation"
    bl_label = "Simplify Objects"

    def execute(self, context):
        remove_inbetween(context, bpy.context.selected_objects)
        return {'FINISHED'}


def remove_inbetween(context, objs):
    step = context.scene.step
    
    for obj in objs:
        if obj.animation_data:  # Check that animation data exists
            action = obj.animation_data.action
            
            if action:  # Check that an action exists
                for fcurve in action.fcurves:
                    keyframe_points = [point for point in fcurve.keyframe_points if point.select_control_point]  # Filter only selected keyframes
                    
                    for i in range(len(keyframe_points) - 1, -1, -1):  # Reverse loop over keyframes
                        if i % step != 0:
                            fcurve.keyframe_points.remove(keyframe_points[i])


def register():
    bpy.utils.register_class(SimplifyAnimationPanel)
    bpy.utils.register_class(SimplifyAnimationOperator)
    bpy.utils.register_class(SimplifyObjectAnimationOperator)
    bpy.types.Scene.step = bpy.props.IntProperty(name = "Step Size", default = 1)

                    
def unregister():
    bpy.utils.unregister_class(SimplifyAnimationPanel)
    bpy.utils.unregister_class(SimplifyAnimationOperator)
    bpy.utils.unregister_class(SimplifyObjectAnimationOperator)
    del bpy.types.Scene.step

    
if __name__ == "__main__":
    register()
