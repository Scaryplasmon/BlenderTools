import bpy
import os
import sys
from PIL import Image
from .utils import generate_image, display_image_as_plane

from diffusers import StableDiffusionControlNetPipeline, ControlNetModel, UniPCMultistepScheduler, LCMScheduler, StableDiffusionXLPipeline, StableDiffusionImg2ImgPipeline, StableDiffusionDepth2ImgPipeline, DiffusionPipeline, StableDiffusionPipeline
from diffusers.utils import load_image, make_image_grid
import torch


# USEFUL LINES for later (❁´◡`❁)
# # pipe.enable_xformers_memory_efficient_attention()
#make_image_grid([original_image, canny_image, output], rows=1, cols=3)
# (VERY SLOW)
# pipe.enable_model_cpu_offload()

#PARAMETERS
type = 'local'  # 'control_CANNY' or 'control_XL'
scheduler='LCM'
device = "cuda" if torch.cuda.is_available() else "NOcpuPlease"
print(device)

input_image_path = "C:/Users/andre/OneDrive/Desktop/tmp/0002.png"
models_path = "C://Users//andre//OneDrive//Desktop//tmp//checkpoints//dreamshaper_8.safetensors"
prompt = "evil monkey looking at plant in a vase near a fire in a dramatic stylized style, pixar, 4k, UHD."
neg_prompt = "ugly, blurry, poor quality"

# PIPELINEs
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

# SCHEDULERs
if scheduler == 'LCM':
    pipe.scheduler = LCMScheduler.from_config(pipe.scheduler.config)
    pipe.to(device)

if scheduler == 'UniPC':
    pipe.scheduler = UniPCMultistepScheduler.from_config(pipe.scheduler.config)
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
generated_image = generate_image(pipeline, lora_id, device, input_image_path, prompt, neg_prompt, num_inference_steps=24, strength=1.0, guidance_scale=7.5, seed=123)
display_image_as_plane(generated_image)
