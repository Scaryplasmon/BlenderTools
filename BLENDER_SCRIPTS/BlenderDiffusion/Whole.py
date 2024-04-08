bl_info = {
    "name": "BlenderDiffusion",
    "blender": (4, 0, 2),
    "category": "Render",
    "description": "Generate images using Diffusion models within Blender",
    "author": "Your Name",
    "version": (1, 0, 0),
    "location": "Properties > Render"
}
import os
import sys
from io import BytesIO
import requests
import imageio
import bpy
from bpy.props import StringProperty, EnumProperty, BoolProperty, IntProperty
from PIL import Image, ImageOps
from diffusers.utils import load_image, export_to_video
from diffusers import (
    StableDiffusionControlNetPipeline, 
    ControlNetModel,
    StableDiffusionXLPipeline,
    StableDiffusionImg2ImgPipeline,
    StableVideoDiffusionPipeline,
    MotionAdapter, 
    AnimateDiffVideoToVideoPipeline
)
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

import torch
import threading
print(torch.cuda.is_available())


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
    
class BlenderDiffusionPanel(bpy.types.Panel):
    bl_label = "BlenderDiffusion"
    bl_idname = "RENDER_PT_blender_diffusion"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"

    def draw(self, context):
        layout = self.layout
        scene = context.scene.sd15

        layout.prop(scene, "sd15_bool")
        layout.prop(scene, "sd15")
        layout.prop(scene, "ctrl_net_bool")
        layout.prop(scene, "ctrl_net")
        layout.prop(scene, "sdxl_bool")
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
        layout.operator("wm.blenderdiffusion_generate_animation")
        layout.operator("wm.blenderdiffusion_generate_video")
        layout.operator("wm.blenderdiffusion_offload")
        
class BlenderDiffusionGenerateOperator(bpy.types.Operator):
    bl_idname = "wm.blenderdiffusion_generate"
    bl_label = "Generate Image"

    def execute(self, context):
        props = context.scene.sd15
        print("Generating Image...")

        # Define a function to run in the background thread
        def generate_in_background():
            pipeline = setup_pipeline(props.diffusion_device.lower(), props.diffusion_scheduler, props.sd15,props.sd15_bool,props.ctrl_net,props.ctrl_net_bool, props.sdxl, props.sdxl_bool, props.FreeU, props.lora_id)
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
    
class BlenderDiffusionGenerateAnimationOperator(bpy.types.Operator):
    bl_idname = "wm.blenderdiffusion_generate_animation"
    bl_label = "Generate Animation"

    def execute(self, context):
        props = context.scene.sd15
        print("Generating Animation...")
        threading.Thread(target=self.generate_animation_in_background, args=(props, context)).start()
        return {'FINISHED'}

    def generate_animation_in_background(self, props, context):
        try:
            # Assuming generate_animation function is defined elsewhere and works correctly
            generated_animation = generate_animation(
                device="cuda" if torch.cuda.is_available() else "cpu",
                input_image_path=props.diffusion_input_image_path,
                prompt=props.diffusion_prompt,
                negative_prompt=props.diffusion_neg_prompt,
                num_inference_steps=props.num_inference_steps,
                strength=props.strength,
                guidance_scale=props.guidance_scale,
                seed=props.seed
            )
            filepath = os.path.join(bpy.path.abspath(context.scene.render.filepath), "generated_animation.mp4")
            # Assuming export_to_video function is defined elsewhere and works correctly
            export_to_video(generated_animation, filepath, fps=7)
            print("Animation saved successfully.", filepath)
        except Exception as e:
            print(f"Failed to generate or save animation: {e}")
            self.save_partial_results(generated_animation, context)

    def save_partial_results(self, generated_animation, context):
        output_path = os.path.join(bpy.path.abspath(context.scene.render.filepath), "partial_generated_frames")
        os.makedirs(output_path, exist_ok=True)
        try:
            for i, frame in enumerate(generated_animation):
                frame_path = os.path.join(output_path, f"frame_{i:04d}.png")
                frame.save(frame_path)
            print("Saved partial frames due to error.")
        except Exception as e:
            print(f"Failed to save partial frames: {e}")
            
class BlenderDiffusionGenerateVideoOperator(bpy.types.Operator):
    bl_idname = "wm.blenderdiffusion_generate_video"
    bl_label = "Generate Video"

    def execute(self, context):
        props = context.scene.sd15
        print("Generating Video...")

        # Define a function to run in the background thread
        def generate_video_in_background():
            generated_video = generate_video(
                device="cuda" if torch.cuda.is_available() else "cpu",
                strength=props.strength,
                seed=props.seed
            )
            try:
                bpy.app.timers.register(lambda: export_to_video(generated_video, "generated.mp4", fps=7))
            except Exception as e:
                print(e)
                export_to_video(generated_video, "generated.mp4", fps=7)

        
        # Start the background thread
        threading.Thread(target=generate_video_in_background).start()

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
    
def setup_pipeline(device, scheduler, sd15 = "runwayml/stable-diffusion-v1-5", sd15_bool = True, ctrl_net = "", ctrl_net_bool = False,  sdxl = "",  sdxl_bool = False, freeU = False, lora_id = "None"):

    device = "cuda" if torch.cuda.is_available() else "NOcpuPlease"
    pipe = None
    #PIPELINE
    print(device)
    if sd15_bool == True and sd15 != "":
        model_id = sd15
        if ctrl_net_bool == True:
            if ctrl_net != "None":
                controlnet = ControlNetModel.from_pretrained(ctrl_net, torch_dtype=torch.float16, use_safetensors=True)
                pipe = StableDiffusionControlNetPipeline.from_pretrained(model_id, controlnet=controlnet, torch_dtype=torch.float16, use_safetensors=True).to(device)
                pipe.enable_xformers_memory_efficient_attention()
        else:
            if model_id != "None":          
                pipe = StableDiffusionImg2ImgPipeline.from_pretrained(model_id, torch_dtype=torch.float16, use_safetensors=True).to(device)
                pipe.enable_xformers_memory_efficient_attention()
    elif sd15_bool== False and sdxl == True:
        model_id = sdxl
        if model_id != "None":
            pipe = StableDiffusionXLPipeline.from_pretrained(model_id, torch_dtype=torch.float16, use_safetensors=True, variant="fp16").to(device)
            pipe.enable_xformers_memory_efficient_attention()
        else:
            print("No model provided")
            
    if pipe is None:
        raise ValueError("No valid model configuration provided. Please check your settings.")

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
    if lora_id == "None":
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
       
def generate_animation(device, input_image_path, prompt, negative_prompt, num_inference_steps=20, strength=0.8, guidance_scale=6.5, seed=12345):

#   # Load the motion adapter
#    adapter = MotionAdapter.from_pretrained("guoyww/animatediff-motion-adapter-v1-5-2", torch_dtype=torch.float16)

    adapter = MotionAdapter.from_pretrained("wangfuyun/AnimateLCM")
    # load SD 1.5 based finetuned model
    model_id = "SG161222/Realistic_Vision_V5.1_noVAE"
#    model_id = "stablediffusionapi/realistic-vision-v60"
    pipe = AnimateDiffVideoToVideoPipeline.from_pretrained(model_id, motion_adapter=adapter, torch_dtype=torch.float16).to("cuda")
    pipe.scheduler = LCMScheduler.from_config(pipe.scheduler.config, beta_schedule="linear")

    # helper function to load videos
    def load_video(file_path: str):
        images = []

        if file_path.startswith(('http://', 'https://')):
            # If the file_path is a URL
            response = requests.get(file_path)
            response.raise_for_status()
            content = BytesIO(response.content)
            vid = imageio.get_reader(content)
        else:
            # Assuming it's a local file path
            vid = imageio.get_reader(file_path)

        for frame in vid:
            pil_image = Image.fromarray(frame)
            images.append(pil_image)

        return images

    video = load_video(input_image_path)

    try:
        pipe.load_lora_weights("wangfuyun/AnimateLCM", weight_name="sd15_lora_beta.safetensors", adapter_name="lcm-lora")
    except:
        print("exception")
    try:
        pipe.load_lora_weights("wangfuyun/AnimateLCM/sd15_lora_beta.safetensors", adapter_name="lcm-lora")
    except:
        print("exception")
    # enable memory savings
    pipe.enable_vae_slicing()
    pipe.enable_model_cpu_offload()

    output = pipe(
        video = video,
        prompt=prompt,
        negative_prompt=negative_prompt,
        guidance_scale=guidance_scale,
        num_inference_steps=num_inference_steps,
        strength=strength,
        generator = torch.Generator(device).manual_seed(seed)
    )
    frames = output.frames[0]
    export_to_video(frames, "animation.mp4", fps=10)
    return frames


def generate_image(pipe, device, input_image_path, prompt, negative_prompt, num_inference_steps=20, strength=0.8, guidance_scale=6.5, seed=12345):

    # Load the input image# SEED
    generator = torch.Generator(device).manual_seed(seed)   

    # InputIMAGE
    input_image = Image.open(input_image_path).convert("RGB")
    
    # GenerateIMAGE
    with torch.no_grad():
        image = pipe(
            prompt=prompt, 
            negative_prompt=negative_prompt, 
            image=input_image, 
            strength=strength, num_inference_steps=num_inference_steps, generator=generator, 
            guidance_scale=guidance_scale,
            requires_safety_checker= False,
        ).images[0]
        
    image = ImageOps.flip(image)
    
    print("Image generated successfully! yay (❁´◡`❁)")
    return image
def generate_video(device, strength=0.8, seed=12345):

    pipe = StableVideoDiffusionPipeline.from_pretrained(
    "stabilityai/stable-video-diffusion-img2vid-xt", torch_dtype=torch.float16, variant="fp16"
    )
    pipe.enable_model_cpu_offload()
    generator = torch.Generator(device).manual_seed(seed)   
    pipe.unet.enable_forward_chunking()
    
    # Load the conditioning image
    image = load_image("https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/diffusers/svd/rocket.png")
    image = image.resize((1024, 576))
    # GenerateIMAGE
    with torch.no_grad():
        frames = pipe(
            image, 
            decode_chunk_size=2, 
            generator=generator, 
            motion_bucket_id=180, 
            noise_aug_strength=strength).frames[0]
        
    export_to_video(frames, "generated.mp4", fps=7)

    
    print("Video generated successfully! yay (❁´◡`❁)")
    return frames

def display_image_as_plane(image, plane_name="GeneratedImagePlane", material_name="GeneratedImageMaterial"):
    # Convert PIL Image to bytes
    image_bytes = image.convert("RGBA").tobytes()
    
    # Create a new image in Blender
    blender_image = bpy.data.images.new(name=plane_name + "Img", width=image.width, height=image.height, alpha=True)
    blender_image.file_format = 'PNG'
    blender_image.pixels = [v / 255 for v in image_bytes]
    
    # Create a new mesh and object
    bpy.ops.mesh.primitive_plane_add(size=2, enter_editmode=False, align='WORLD', location=(0, 0, 0), rotation=(0, 0, 180), scale=(-1, 1, 1)), 
    plane = bpy.context.active_object
    plane.name = plane_name

    # Create a new material with a Principled BSDF shader
    mat = bpy.data.materials.new(name=material_name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')

    # Create an image texture node and load the blender image
    tex_image = mat.node_tree.nodes.new('ShaderNodeTexImage')
    tex_image.image = blender_image

    # Link the image texture node to the BSDF shader
    mat.node_tree.links.new(bsdf.inputs['Base Color'], tex_image.outputs['Color'])

    # Assign the material to the plane
    if plane.data.materials:
        plane.data.materials[0] = mat
    else:
        plane.data.materials.append(mat)

def register():
    bpy.utils.register_class(BlenderDiffusionProperties)
    bpy.types.Scene.sd15 = bpy.props.PointerProperty(type=BlenderDiffusionProperties)
    bpy.utils.register_class(BlenderDiffusionPanel)
    bpy.utils.register_class(BlenderDiffusionGenerateOperator)
    bpy.utils.register_class(BlenderDiffusionGenerateAnimationOperator)
    bpy.utils.register_class(BlenderDiffusionGenerateVideoOperator)
    bpy.utils.register_class(BlenderDiffusionOffloadOperator)

def unregister():
    del bpy.types.Scene.sd15
    bpy.utils.unregister_class(BlenderDiffusionProperties)
    bpy.utils.unregister_class(BlenderDiffusionPanel)
    bpy.utils.unregister_class(BlenderDiffusionGenerateOperator)
    bpy.utils.unregister_class(BlenderDiffusionGenerateAnimationOperator)
    bpy.utils.unregister_class(BlenderDiffusionGenerateVideoOperator)
    bpy.utils.unregister_class(BlenderDiffusionOffloadOperator)

if __name__ == "__main__":
    register()
