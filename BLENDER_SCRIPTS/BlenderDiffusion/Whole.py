import bpy
import os
import sys

import torch
from PIL import Image
from diffusers import StableDiffusionControlNetPipeline, ControlNetModel, UniPCMultistepScheduler, LCMScheduler, StableDiffusionXLPipeline, StableDiffusionImg2ImgPipeline, StableDiffusionDepth2ImgPipeline, DiffusionPipeline, StableDiffusionPipeline

freeU = True
#PARAMETERS
type = 'local'  # 'control_CANNY' or 'control_XL'
scheduler='LCM'
device = "cuda" if torch.cuda.is_available() else "NOcpuPlease"
print(device)

input_image_path = "C:/Users/andre/OneDrive/Desktop/tmp/0002.png"
models_path = "C://Users//andre//OneDrive//Desktop//tmp//checkpoints//dreamshaper_8.safetensors"
prompt = "evil monkey looking at plant in a vase near a fire in a dramatic stylized style, pixar, 4k, UHD."
neg_prompt = "ugly, blurry, poor quality"

def generate_image(pipe, device, input_image_path, prompt, negative_prompt, num_inference_steps=24, strength=1.0, guidance_scale=7.5, seed=12345):

    # Load the input image# SEED
    generator = torch.Generator(device).manual_seed(seed)   

    # FreeU
    if freeU == True:
        #tends to saturate the pictures a lot! great for stylized outputs
        pipe.enable_freeu(s1=0.9, s2=0.2, b1=1.2, b2=1.4)

    # InputIMAGE
    input_image = Image.open(input_image_path).convert("RGB")
    
    # GenerateIMAGE
    with torch.no_grad():
        image = pipe(
            prompt=prompt, 
            negative_prompt=negative_prompt, 
            image=input_image, 
            strength=strength, num_inference_steps=num_inference_steps, generator=generator, 
            guidance_scale=guidance_scale
        ).images[0]
    
    return image

def display_image_as_plane(image, plane_name="GeneratedImagePlane", material_name="GeneratedImageMaterial"):
    # Convert PIL Image to bytes
    image_bytes = image.convert("RGBA").tobytes()
    
    # Create a new image in Blender
    blender_image = bpy.data.images.new(name=plane_name + "Img", width=image.width, height=image.height, alpha=True)
    blender_image.file_format = 'PNG'
    blender_image.pixels = [v / 255 for v in image_bytes]
    
    # Create a new mesh and object
    bpy.ops.mesh.primitive_plane_add(size=-2)
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



# PIPELINE
if type == 'control_CANNY':
    controlnet = ControlNetModel.from_pretrained("lllyasviel/sd-controlnet-canny", torch_dtype=torch.float16, use_safetensors=True)
    model_id="runwayml/stable-diffusion-v1-5"
    pipe = StableDiffusionControlNetPipeline.from_pretrained(
        model_id = model_id, 
        controlnet=controlnet, 
        torch_dtype=torch.float16, 
        use_safetensors=True
    )

elif type == 'SSD-1B':
    # not the right controlnet
    # controlnet = ControlNetModel.from_pretrained("lllyasviel/sd-controlnet-canny", torch_dtype=torch.float16, use_safetensors=True)
    model_id="segmind/SSD-1B"
    pipe = StableDiffusionXLPipeline.from_pretrained(
        model_id=model_id, 
        torch_dtype=torch.float16, 
        use_safetensors=True, 
        variant="fp16"
    )

elif type == 'SD2':
    # Load the pipeline
    model_id = "stabilityai/stable-diffusion-2-base"
    pipe = StableDiffusionImg2ImgPipeline.from_pretrained(model_id).to(device)
    print(model_id)

elif type == 'local':
    # local path in your computer
    model_id = models_path
    pipe = StableDiffusionPipeline.from_single_file(model_id, torch_dtype=torch.float16, 
        use_safetensors=True).to(device)
    print(model_id)
    
else:
    model_id = "stabilityai/stable-diffusion-2-depth"
    pipe = StableDiffusionDepth2ImgPipeline.from_pretrained(model_id).to(device)
    print(model_id)

# SCHEDULER
if scheduler == 'LCM':
    pipe.scheduler = LCMScheduler.from_config(pipe.scheduler.config)
    pipe.to(device)
else:
    pipe.scheduler = UniPCMultistepScheduler.from_config(pipe.scheduler.config)
    pipe.to(device)
    
#LORA
lora_id = "latent-consistency/lcm-lora-sdv1-5"
pipe.load_lora_weights(lora_id)
pipe.fuse_lora()

#GenerateImage (call utils.py)
pipeline = pipe
generated_image = generate_image(pipeline, device, input_image_path, prompt, neg_prompt, num_inference_steps=24, strength=1.0, guidance_scale=7.5, seed=123)
display_image_as_plane(generated_image)
