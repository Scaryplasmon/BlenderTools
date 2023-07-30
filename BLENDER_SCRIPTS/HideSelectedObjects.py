import bpy

def hide_selected_objects(context):
    # get the selected objects
    selected_objects = context.selected_objects

    # hide the objects and keyframe their visibility
    for obj in selected_objects:
        obj.hide_viewport = True
        obj.hide_render = True
        if not obj.animation_data:
            obj.animation_data_create()
        if not obj.animation_data.action:
            obj.animation_data.action = bpy.data.actions.new(name="Visibility")
        obj.keyframe_insert(data_path="hide_render", frame=context.scene.frame_current)
        obj.keyframe_insert(data_path="hide_viewport", frame=context.scene.frame_current)
def show_selected_objects(context):
    # get the selected objects
    selected_objects = context.selected_objects

    # show the objects and keyframe their visibility
    for obj in selected_objects:
        obj.hide_viewport = False
        obj.hide_render = False
        if not obj.animation_data:
            obj.animation_data_create()
        if not obj.animation_data.action:
            obj.animation_data.action = bpy.data.actions.new(name="Visibility")
        obj.keyframe_insert(data_path="hide_render", frame=context.scene.frame_current)
        obj.keyframe_insert(data_path="hide_viewport", frame=context.scene.frame_current)
        
# create the buttons in the Object Properties panel
class OBJECT_PT_visibility_controls(bpy.types.Panel):
    bl_label = "Visibility Controls"
    bl_idname = "OBJECT_PT_visibility_controls"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    def draw(self, context):
        layout = self.layout
        layout.operator("object.hide_objects", text="Hide Selected Objects")
        layout.operator("object.show_objects", text="Show Selected Objects")

# create the operators that will be called when the buttons are pressed
class OBJECT_OT_hide_objects(bpy.types.Operator):
    bl_idname = "object.hide_objects"
    bl_label = "Hide Selected Objects"
    bl_description = "Hide the selected objects and keyframe their visibility"

    def execute(self, context):
        hide_selected_objects(context)
        return {'FINISHED'}

class OBJECT_OT_show_objects(bpy.types.Operator):
    bl_idname = "object.show_objects"
    bl_label = "Show Selected Objects"
    bl_description = "Show the selected objects and keyframe their visibility"

    def execute(self, context):
        show_selected_objects(context)
        return {'FINISHED'}

# register the classes and the operators
def register():
    bpy.utils.register_class(OBJECT_PT_visibility_controls)
    bpy.utils.register_class(OBJECT_OT_hide_objects)
    bpy.utils.register_class(OBJECT_OT_show_objects)

def unregister():
    bpy.utils.unregister_class(OBJECT_PT_visibility_controls)
    bpy.utils.unregister_class(OBJECT_OT_hide_objects)
    bpy.utils.unregister_class(OBJECT_OT_show_objects)


if __name__ == "__main__":
    register()
