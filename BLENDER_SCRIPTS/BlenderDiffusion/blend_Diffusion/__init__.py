import bpy
import os
import sys
from . import main

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
    diffusion_type: bpy.props.EnumProperty(
        name="Type",
        description="Choose the type of diffusion",
        items=[('control_CANNY', "Control CANNY", ""),
               ('SSD_1B', "SSD-1B", ""),
               ('SD2', "SD2", ""),
               ('LOCAL', "Local", "")]
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
    diffusion_models_path: bpy.props.StringProperty(
        name="Models Path",
        description="Path to the models directory",
        subtype='DIR_PATH'
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
    bpy.types.Scene.blenderdiffusion = bpy.props.PointerProperty(type=BlenderDiffusionProperties)
    main.register()

def unregister():
    del bpy.types.Scene.blenderdiffusion
    bpy.utils.unregister_class(BlenderDiffusionProperties)
    main.unregister()

if __name__ == "__main__":
    register()
