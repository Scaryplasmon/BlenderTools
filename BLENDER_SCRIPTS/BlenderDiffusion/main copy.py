#BLEND
import bpy
from bpy.props import StringProperty, EnumProperty
from .utils import generate_image, display_image_as_plane

#PIPELINES
from diffusers import (
    StableDiffusionControlNetPipeline, 
    ControlNetModel,
    StableDiffusionXLPipeline,
    StableDiffusionImg2ImgPipeline
)
# #past
# StableDiffusionDepth2ImgPipeline,
# StableDiffusionPipeline,
# DiffusionPipeline

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

        layout.prop(scene, "sd15")
        layout.prop(scene, "ctrl_net")
        layout.prop(scene, "sdxl")
        layout.prop(scene, "lora_id")
        layout.prop(scene, "FreeU")
        layout.prop(scene, "diffusion_scheduler")
        layout.prop(scene, "diffusion_device")
        layout.prop(scene, "diffusion_input_image_path")
        layout.prop(scene, "diffusion_prompt")
        layout.prop(scene, "diffusion_neg_prompt")
        layout.prop(scene, "num_inference_steps")
        layout.prop(scene, "strength")
        layout.prop(scene, "guidance_scale")
        layout.prop(scene, "seed")

        layout.operator("wm.blenderdiffusion_generate")
        layout.operator("wm.blenderdiffusion_offload")
        
# #toINTEGRATEyet
# class BakeDepth(bpy.types.Operator):
#     obj = bpy.context.active_object
#     # You can choose your texture size (This will be the de bake image)
#     image_name = obj.name + '_BakedTexture'
#     img = bpy.data.images.new(image_name,512,512)

    
#     #Due to the presence of any multiple materials, it seems necessary to iterate on all the materials, and assign them a node + the image to bake.
#     for mat in obj.data.materials:

#         mat.use_nodes = True #Here it is assumed that the materials have been created with nodes, otherwise it would not be possible to assign a node for the Bake, so this step is a bit useless
#         nodes = mat.node_tree.nodes
#         texture_node =nodes.new('ShaderNodeTexImage')
#         texture_node.name = 'Bake_node'
#         texture_node.select = True
#         nodes.active = texture_node
#         texture_node.image = img #Assign the image to the node
        
#     bpy.context.view_layer.objects.active = obj
#     bpy.ops.object.bake(type='DIFFUSE', save_mode='EXTERNAL')

#     img.save_render(filepath='C:\\TEMP\\baked.png')
        
#     #In the last step, we are going to delete the nodes we created earlier
#     for mat in obj.data.materials:
#         for n in mat.node_tree.nodes:
#             if n.name == 'Bake_node':
#                 mat.node_tree.nodes.remove(n)

class BlenderDiffusionGenerateOperator(bpy.types.Operator):
    bl_idname = "wm.blenderdiffusion_generate"
    bl_label = "Generate Image"

    def execute(self, context):
        props = context.scene.blenderdiffusion

        # Define a function to run in the background thread
        def generate_in_background():
            pipeline = setup_pipeline(props.diffusion_device.lower(), props.diffusion_scheduler, props.sd15,props.ctrl_net, props.sdxl, props.FreeU, props.lora_id)
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
    
def setup_pipeline(device, scheduler, sd15 = "", ctrl_net = "", sdxl = "", freeU = False, lora_id = ""):

    device = "cuda" if torch.cuda.is_available() else "NOcpuPlease"
    #PIPELINE
    print(device)
    if not sdxl and sd15:
        model_id = sd15
        if ctrl_net:
            controlnet = ControlNetModel.from_pretrained(ctrl_net, torch_dtype=torch.float16, use_safetensors=True)
            pipe = StableDiffusionControlNetPipeline.from_pretrained(model_id, controlnet=controlnet, torch_dtype=torch.float16, use_safetensors=True).to(device)
            pipe.enable_xformers_memory_efficient_attention()
        else:
            pipe = StableDiffusionImg2ImgPipeline.from_pretrained(model_id, torch_dtype=torch.float16, use_safetensors=True).to(device)
            pipe.enable_xformers_memory_efficient_attention()
    elif not sd15 and sdxl:
        model_id = sdxl
        pipe = StableDiffusionXLPipeline.from_pretrained(model_id, torch_dtype=torch.float16, use_safetensors=True, variant="fp16").to(device)
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
#LORA
    if not lora_id:
        print("No LORA ID provided")
    else:
        pipe.load_lora_weights(lora_id)
        pipe.fuse_lora()
#FREEU
    if freeU == True:
        #tends to saturate the pictures a lot! great for stylized outputs
        pipe.enable_freeu(s1=0.9, s2=0.2, b1=1.2, b2=1.4)
    #just making sure xformers kicks in, everyday is a good day for xformers    
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

