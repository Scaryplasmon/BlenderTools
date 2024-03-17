import bpy
from bpy.props import StringProperty, EnumProperty
from .utils import display_image_as_plane, generate_image
from diffusers import (StableDiffusionControlNetPipeline, ControlNetModel,
                       LCMScheduler, UniPCMultistepScheduler, StableDiffusionXLPipeline,
                       StableDiffusionImg2ImgPipeline, StableDiffusionDepth2ImgPipeline,
                       StableDiffusionPipeline)
import torch


def setup_pipeline(diffusion_type, models_path, device, scheduler):

    device = "cuda" if torch.cuda.is_available() else "NOcpuPlease"
    #PIPELINE
    print(device)
    if diffusion_type == 'control_CANNY':
        controlnet = ControlNetModel.from_pretrained("lllyasviel/sd-controlnet-canny", torch_dtype=torch.float16, use_safetensors=True)
        model_id = "runwayml/stable-diffusion-v1-5"
        pipe = StableDiffusionControlNetPipeline.from_pretrained(model_id, controlnet=controlnet, torch_dtype=torch.float16, use_safetensors=True)

    elif diffusion_type == 'SSD-1B':
        model_id = "segmind/SSD-1B"
        pipe = StableDiffusionXLPipeline.from_pretrained(model_id, torch_dtype=torch.float16, use_safetensors=True, variant="fp16")

    elif diffusion_type == 'SD2':
        model_id = "stabilityai/stable-diffusion-2-base"
        pipe = StableDiffusionImg2ImgPipeline.from_pretrained(model_id)

    elif diffusion_type == 'local':
        model_id = models_path
        pipe = StableDiffusionPipeline.from_single_file(model_id, torch_dtype=torch.float16, use_safetensors=True)

    else:
        # Default to SD2 if no type matches
        model_id = "stabilityai/stable-diffusion-2-base"
        pipe = StableDiffusionImg2ImgPipeline.from_pretrained(model_id)

    #SCHEDULERs
    if scheduler == 'LCM':
        pipe.scheduler = LCMScheduler.from_config(pipe.scheduler.config)
    elif scheduler == 'UniPC':
        pipe.scheduler = UniPCMultistepScheduler.from_config(pipe.scheduler.config)

    pipe.to(device)
    return pipe
class BlenderDiffusionPanel(bpy.types.Panel):
    bl_label = "BlenderDiffusion"
    bl_idname = "RENDER_PT_blender_diffusion"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"

    def draw(self, context):
        layout = self.layout
        scene = context.scene.blenderdiffusion

        layout.prop(scene, "diffusion_type")
        layout.prop(scene, "diffusion_scheduler")
        layout.prop(scene, "diffusion_device")
        layout.prop(scene, "diffusion_input_image_path")
        layout.prop(scene, "diffusion_models_path")
        layout.prop(scene, "diffusion_prompt")
        layout.prop(scene, "diffusion_neg_prompt")

        layout.prop(scene, "num_inference_steps")
        layout.prop(scene, "strength")
        layout.prop(scene, "guidance_scale")
        layout.prop(scene, "seed")

        layout.operator("wm.blenderdiffusion_generate")
        layout.operator("wm.blenderdiffusion_offload")


class BlenderDiffusionGenerateOperator(bpy.types.Operator):
    bl_idname = "wm.blenderdiffusion_generate"
    bl_label = "Generate Image"

    def execute(self, context):
        props = context.scene.blenderdiffusion
        pipeline = setup_pipeline(props.diffusion_type, props.diffusion_models_path, props.diffusion_device.lower(), props.diffusion_scheduler)

        generated_image = generate_image(
            pipe=pipeline,
            device=props.diffusion_device.lower(),
            input_image_path=props.diffusion_input_image_path,
            prompt=props.diffusion_prompt,
            negative_prompt=props.diffusion_neg_prompt,
            num_inference_steps=props.num_inference_steps,
            strength=props.strength,
            guidance_scale=props.guidance_scale,
            seed=props.seed
        )
        display_image_as_plane(generated_image)
        return {'FINISHED'}
    
class BlenderDiffusionOffloadOperator(bpy.types.Operator):
    bl_idname = "wm.blenderdiffusion_offload"
    bl_label = "Offload Model and Refresh VRAM"

    @staticmethod
    def offload_model():
        torch.cuda.empty_cache()
        
    def execute(self, context):
        self.offload_model()
        self.report({'INFO'}, "Model offloaded and VRAM refreshed.")
        return {'FINISHED'}

def register():
    bpy.utils.register_class(BlenderDiffusionPanel)
    bpy.utils.register_class(BlenderDiffusionGenerateOperator)
    bpy.utils.register_class(BlenderDiffusionOffloadOperator)

def unregister():
    bpy.utils.unregister_class(BlenderDiffusionPanel)
    bpy.utils.unregister_class(BlenderDiffusionGenerateOperator)
    bpy.utils.unregister_class(BlenderDiffusionOffloadOperator)

