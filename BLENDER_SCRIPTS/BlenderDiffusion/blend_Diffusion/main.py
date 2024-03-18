#BLEND
import bpy
from bpy.props import StringProperty, EnumProperty
from .utils import generate_image, display_image_as_plane

#PIPELINES
from diffusers import (
    StableDiffusionControlNetPipeline, 
    ControlNetModel,
    StableDiffusionXLPipeline,
    StableDiffusionImg2ImgPipeline, 
    StableDiffusionDepth2ImgPipeline,
    StableDiffusionPipeline,
    DiffusionPipeline
)

#SCHEDULERS
from diffusers import (
    DDPMScheduler,
    DDIMScheduler,
    PNDMScheduler,
    LMSDiscreteScheduler,
    EulerAncestralDiscreteScheduler,
    EulerDiscreteScheduler,
    DPMSolverMultistepScheduler,
    LCMScheduler, 
    UniPCMultistepScheduler,
)

#MAIN
import torch
import threading


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

        # Define a function to run in the background thread
        def generate_in_background():
            pipeline = setup_pipeline(props.diffusion_type, props.diffusion_models_path, props.diffusion_device.lower(), props.diffusion_scheduler)
            generated_image = generate_image(
                pipe=pipeline,
                device="cuda" if torch.cuda.is_available() else "cpu",
                input_image_path=props.diffusion_input_image_path,
                prompt=props.diffusion_prompt,
                negative_prompt=props.diffusion_neg_prompt,
                num_inference_steps=props.num_inference_steps,
                strength=props.strength,
                guidance_scale=props.guidance_scale,
                seed=props.seed
            )
            try:
                bpy.app.timers.register(lambda: display_image_as_plane(generated_image))
            except Exception as e:
                print(e)
                display_image_as_plane(generated_image)

        # Start the background thread
        threading.Thread(target=generate_in_background).start()

        return {'FINISHED'}

    
def setup_pipeline(diffusion_type, models_path, device, scheduler):

    device = "cuda" if torch.cuda.is_available() else "NOcpuPlease"
    #PIPELINE
    print(device)
    if diffusion_type == 'control_CANNY':
        controlnet = ControlNetModel.from_pretrained("lllyasviel/sd-controlnet-canny", torch_dtype=torch.float16, use_safetensors=True)
        model_id = "runwayml/stable-diffusion-v1-5"
        pipe = StableDiffusionControlNetPipeline.from_pretrained(model_id, controlnet=controlnet, torch_dtype=torch.float16, use_safetensors=True).to(device)

        pipe.enable_xformers_memory_efficient_attention()

    elif diffusion_type == 'SSD-1B':
        model_id = "segmind/SSD-1B"
        pipe = StableDiffusionXLPipeline.from_pretrained(model_id, torch_dtype=torch.float16, use_safetensors=True, variant="fp16").to(device)

        pipe.enable_xformers_memory_efficient_attention()


    elif diffusion_type == 'SD2':
        model_id = "stabilityai/stable-diffusion-2-base"
        pipe = StableDiffusionImg2ImgPipeline.from_pretrained(model_id).to(device)

        pipe.enable_xformers_memory_efficient_attention()


    elif diffusion_type == 'local':
        model_id = models_path
        pipe = StableDiffusionImg2ImgPipeline.from_single_file(model_id, torch_dtype=torch.float16, use_safetensors=True).to(device)

        pipe.enable_xformers_memory_efficient_attention()


    else:
        # Default to SD2 if no type matches
        model_id = "runwayml/stable-diffusion-v1-5"
        pipe = StableDiffusionImg2ImgPipeline.from_pretrained(model_id).to(device)

        pipe.enable_xformers_memory_efficient_attention()


    #SCHEDULERs
    if scheduler == 'LCM':
        pipe.scheduler = LCMScheduler.from_config(pipe.scheduler.config)
    elif scheduler == 'UniPC':
        pipe.scheduler = UniPCMultistepScheduler.from_config(pipe.scheduler.config)
    elif scheduler == 'DPMSolver':
        pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
    elif scheduler == 'EulerDiscrete':
        pipe.scheduler = EulerDiscreteScheduler.from_config(pipe.scheduler.config)
    elif scheduler == 'EulerAncestralDiscrete':
        pipe.scheduler = EulerAncestralDiscreteScheduler.from_config(pipe.scheduler.config)
    elif scheduler == 'LMSDiscrete':
        pipe.scheduler = LMSDiscreteScheduler.from_config(pipe.scheduler.config)
    elif scheduler == 'PNDM':
        pipe.scheduler = PNDMScheduler.from_config(pipe.scheduler.config)
    elif scheduler == 'DDIM':
        pipe.scheduler = DDIMScheduler.from_config(pipe.scheduler.config)
    else:
        pipe.scheduler = DDPMScheduler.from_config(pipe.scheduler.config)

    
    pipe.enable_xformers_memory_efficient_attention()
    print(pipe)
    return pipe
   
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

