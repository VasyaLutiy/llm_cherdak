from diffusers import AutoPipelineForText2Image
import torch

pipe = AutoPipelineForText2Image.from_pretrained("stabilityai/sdxl-turbo", torch_dtype=torch.float16, variant="fp16")
pipe.to("cuda")

prompt = """In a cinematic digital painting, Sabrina, dressed in elegant mage robes, is accompanied by her whimsical pet in a serene, lush forest filled with towering trees and intricate foliage. The sunlight filters through the canopy, casting dappled shadows on the forest floor while birds chirp and small creatures rustle about.
"""

image = pipe(prompt=prompt, num_inference_steps=1, guidance_scale=0.0).images[0]
image.save("astronaut_rides_horse.png")
