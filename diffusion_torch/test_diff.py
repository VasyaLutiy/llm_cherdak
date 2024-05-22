import torch
from torch import autocast
from diffusers import StableDiffusionPipeline

model_id = "stabilityai/sdxl-turbo"
device = "cuda"

# the middle two arguments configure the usage of float16 instead of the default float32
pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16, revision="fp16", use_auth_token=True)
pipe = pipe.to(device)

prompt = """Sabrina, a human mage with a funny pet, stands in a lush, vibrant forest with towering trees. The leaves shimmer and glow in the dappled sunlight filtering through the branches. The scene is filled with rich, vibrant colors and a fantasy atmosphere. The mage is wearing elegant robes, and her pet has a whimsical appearance, adding a touch of humor to the scene. The forest is depicted with intricate, highly detailed foliage, creating a magical and serene environment. The overall style is reminiscent of a cinematic digital painting, with sharp focus and an elegant, matte finish.
"""
with autocast("cuda"):
    image = pipe(prompt, guidance_scale=7.5)["images"][0]  # Changed from "sample" to "images"

image.save("astronaut_rides_horse.png")
