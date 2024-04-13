import bpy
import os
import sys
from . import main
from bpy.props import StringProperty, EnumProperty, BoolProperty, IntProperty
bl_info = {
    "name": "BlenderDiffusion",
    "blender": (4, 0, 2),
    "category": "Render",
    "description": "Generate images using Diffusion models within Blender",
    "author": "Your Name",
    "version": (1, 0, 0),
    "location": "Properties > Render"
}

class BlenderDiffusionProperties(bpy.types.PropertyGroup):
    sd15: bpy.props.StringProperty(
        name="sd15",
        description="paste in the model path",
        default="runwayml/stable-diffusion-v1-5"
    )
    sd15_bool: bpy.props.BoolProperty(
        name="sd15_bool",
        description="paste in the model path",
        default=True
    )
    ctrl_net: bpy.props.StringProperty(
        name="ctrl_net",
        description="paste in the model path",
        default="None"
    )
    ctrl_net_bool: bpy.props.BoolProperty(
        name="ctrl_net_bool",
        description="paste in the model path",
        default=False
    )
    sdxl: bpy.props.StringProperty(
        name="sdxl",
        description="paste in the model path",
        default="None"
    )
    sdxl_bool: bpy.props.BoolProperty(
        name="sdxl_bool",
        description="paste in the model path",
        default=False
    )

    lora_id: bpy.props.StringProperty(
        name="lora_id",
        description="paste in the model path",
        default=""
    )
    FreeU: bpy.props.BoolProperty(
        name="FreeU",
        description="Enable FreeU",
        default=False
    )
    diffusion_scheduler: bpy.props.EnumProperty(
        name="Scheduler",
        description="Choose the scheduler",
        items=[('LCM', "LCM", ""),
               ('UNIPC', "UniPC", "")]
    )
    diffusion_device: bpy.props.EnumProperty(
        name="Device",
        description="Choose the device",
        items=[('CUDA', "Cuda", ""),
               ('CPU', "CPU", "")]
    )
    diffusion_input_image_path: bpy.props.StringProperty(
        name="Input Image Path",
        description="Path to the input image",
        subtype='FILE_PATH'
    )
    diffusion_prompt: bpy.props.StringProperty(
        name="Prompt",
        description="Enter a prompt",
        default=""
    )
    diffusion_neg_prompt: bpy.props.StringProperty(
        name="Negative Prompt",
        description="Enter a negative prompt",
        default=""
    )
    num_inference_steps: bpy.props.IntProperty(
        name="Num Inference Steps",
        description="Number of inference steps",
        default=20,
        min=1,
        max=100
    )
    strength: bpy.props.FloatProperty(
        name="Strength",
        description="Strength of the image modification",
        default=0.8,
        min=0.0,
        max=1.0
    )
    guidance_scale: bpy.props.FloatProperty(
        name="Guidance Scale",
        description="Guidance scale",
        default=6.5,
        min=0.0,
        max=20.0
    )
    seed: bpy.props.IntProperty(
        name="Seed",
        description="Seed for the random number generator",
        default=12345
    )

def register():
    bpy.utils.register_class(BlenderDiffusionProperties)
    bpy.types.Scene.sd15 = bpy.props.PointerProperty(type=BlenderDiffusionProperties)
    main.register()

def unregister():
    del bpy.types.Scene.sd15
    bpy.utils.unregister_class(BlenderDiffusionProperties)
    main.unregister()

if __name__ == "__main__":
    register()
