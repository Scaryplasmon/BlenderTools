# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name" : "PaintModifiers",
    "author" : "ScaryPlasmon", 
    "description" : "Paint your modifiers, all the cool kids are doing it!",
    "blender" : (3, 0, 0),
    "version" : (1, 0, 0),
    "location" : "3DView",
    "warning" : "",
    "doc_url": "", 
    "tracker_url": "", 
    "category" : "Paint" 
}


import bpy
import bpy.utils.previews


addon_keymaps = {}
_icons = None
class SNA_MT_DBA6E(bpy.types.Menu):
    bl_idname = "SNA_MT_DBA6E"
    bl_label = ""

    @classmethod
    def poll(cls, context):
        return not (False)

    def draw(self, context):
        layout = self.layout.menu_pie()
        layout.label(text='PaintModifiers', icon_value=793)
        box_54BE4 = layout.box()
        box_54BE4.alert = False
        box_54BE4.enabled = True
        box_54BE4.active = True
        box_54BE4.use_property_split = False
        box_54BE4.use_property_decorate = True
        box_54BE4.alignment = 'Expand'.upper()
        box_54BE4.scale_x = 1.0
        box_54BE4.scale_y = 1.0
        box_54BE4.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
        op = box_54BE4.operator('sna.paintdecimate_a165a', text='PaintDecimate', icon_value=796, emboss=True, depress=False)
        op = box_54BE4.operator('sna.paintdisplace_7c5e2', text='PaintDisplace', icon_value=791, emboss=True, depress=False)
        op = box_54BE4.operator('sna.paintsolidify_29967', text='PaintSolidify', icon_value=786, emboss=True, depress=False)
        op = box_54BE4.operator('sna.paintsmooth_a7d30', text='PaintSmooth', icon_value=785, emboss=True, depress=False)
        op = box_54BE4.operator('object.apply_all_modifiers', text='ApplyModifiers', icon_value=706, emboss=True, depress=False)
        op = box_54BE4.operator('object.delete_all_modifiers', text='DeleteModifiers', icon_value=3, emboss=True, depress=False)


class SNA_OT_Paintsmooth_A7D30(bpy.types.Operator):
    bl_idname = "sna.paintsmooth_a7d30"
    bl_label = "PaintSmooth"
    bl_description = "Paint Smooth group"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return not False

    def execute(self, context):
        bpy.ops.object.modifier_add(type='SMOOTH')
        ob = bpy.context.active_object
        ob.vertex_groups.new(name='Smoothie')
        active = ob.vertex_groups.active
        mi = active.name
        active_m = ob.modifiers.active
        active_modifier = bpy.types.ObjectModifiers(active_m)
        ci = active_modifier.name
        if active_modifier:
            print(ci)
        ob.modifiers[ci].vertex_group = mi
        ob.modifiers[ci].factor = 1.0
        ob.modifiers[ci].iterations = 8    
        bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class SNA_OT_Paintsolidify_29967(bpy.types.Operator):
    bl_idname = "sna.paintsolidify_29967"
    bl_label = "PaintSolidify"
    bl_description = "Paint Solidify group"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return not False

    def execute(self, context):
        bpy.ops.object.modifier_add(type='SOLIDIFY')
        ob = bpy.context.active_object
        ob.vertex_groups.new(name='Solidify')
        active = ob.vertex_groups.active
        mi = active.name
        active_m = ob.modifiers.active
        active_modifier = bpy.types.ObjectModifiers(active_m)
        ci = active_modifier.name
        if active_modifier:
            print(ci)
        ob.modifiers[ci].vertex_group = mi
        ob.modifiers[ci].thickness = 0.1
        ob.modifiers[ci].offset = 1.0
        ob.modifiers[ci].use_rim_only = True
        bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class SNA_OT_Paintdisplace_7C5E2(bpy.types.Operator):
    bl_idname = "sna.paintdisplace_7c5e2"
    bl_label = "PaintDisplace"
    bl_description = "Paint Displace group"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return not False

    def execute(self, context):
        bpy.ops.object.modifier_add(type='DISPLACE')
        ob = bpy.context.active_object
        ob.vertex_groups.new(name='Displace')
        active = ob.vertex_groups.active
        mi = active.name
        active_m = ob.modifiers.active
        active_modifier = bpy.types.ObjectModifiers(active_m)
        ci = active_modifier.name
        if active_modifier:
            print(ci)
        ob.modifiers[ci].vertex_group = mi
        bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class SNA_OT_Paintdecimate_A165A(bpy.types.Operator):
    bl_idname = "sna.paintdecimate_a165a"
    bl_label = "PaintDecimate"
    bl_description = "Paint Decimate group"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return not False

    def execute(self, context):
        bpy.ops.object.modifier_add(type='DECIMATE')
        ob = bpy.context.active_object
        ob.vertex_groups.new(name='Decimate')
        active = ob.vertex_groups.active
        mi = active.name
        active_m = ob.modifiers.active
        active_modifier = bpy.types.ObjectModifiers(active_m)
        ci = active_modifier.name
        if active_modifier:
            print(ci)
        ob.modifiers[ci].vertex_group = mi
        ob.modifiers[ci].ratio = 0.667   
        bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


def register():
    global _icons
    _icons = bpy.utils.previews.new()
    bpy.utils.register_class(SNA_MT_DBA6E)
    bpy.utils.register_class(SNA_OT_Paintsmooth_A7D30)
    bpy.utils.register_class(SNA_OT_Paintsolidify_29967)
    bpy.utils.register_class(SNA_OT_Paintdisplace_7C5E2)
    bpy.utils.register_class(SNA_OT_Paintdecimate_A165A)
    kc = bpy.context.window_manager.keyconfigs.addon
    km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
    kmi = km.keymap_items.new('wm.call_menu_pie', 'V', 'PRESS',
        ctrl=False, alt=True, shift=False, repeat=False)
    kmi.properties.name = 'SNA_MT_DBA6E'
    addon_keymaps['097A9'] = (km, kmi)


def unregister():
    global _icons
    bpy.utils.previews.remove(_icons)
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    for km, kmi in addon_keymaps.values():
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
    bpy.utils.unregister_class(SNA_MT_DBA6E)
    bpy.utils.unregister_class(SNA_OT_Paintsmooth_A7D30)
    bpy.utils.unregister_class(SNA_OT_Paintsolidify_29967)
    bpy.utils.unregister_class(SNA_OT_Paintdisplace_7C5E2)
    bpy.utils.unregister_class(SNA_OT_Paintdecimate_A165A)