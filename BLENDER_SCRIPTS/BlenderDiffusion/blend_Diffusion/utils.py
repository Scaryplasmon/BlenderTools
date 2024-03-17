# utils.py
import bpy
import os
import sys
from PIL import Image
import torch

from diffusers.utils import load_image


freeU = False


def generate_image(pipe, device, input_image_path, prompt, negative_prompt, num_inference_steps=20, strength=0.8, guidance_scale=6.5, seed=12345):

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
    
    print("Image generated successfully! yay (❁´◡`❁)")
    return image

def display_image_as_plane(image, plane_name="GeneratedImagePlane", material_name="GeneratedImageMaterial"):
    # Convert PIL Image to bytes
    image_bytes = image.convert("RGBA").tobytes()
    
    # Create a new image in Blender
    blender_image = bpy.data.images.new(name=plane_name + "Img", width=image.width, height=image.height, alpha=True)
    blender_image.file_format = 'PNG'
    blender_image.pixels = [v / 255 for v in image_bytes]
    
    # Create a new mesh and object
    bpy.ops.mesh.primitive_plane_add(size=2, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
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