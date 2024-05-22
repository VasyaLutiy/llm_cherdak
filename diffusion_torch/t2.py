from pathlib import Path
import tqdm

import torch
import pandas as pd
import numpy as np
from diffusers import StableDiffusionPipeline
from transformers import pipeline, set_seed
import matplotlib.pyplot as plt

from kaggle_secrets import UserSecretsClient


class CFG:
    device = "cuda"
    seed = 42
    generator = torch.Generator(device).manual_seed(seed)
    image_gen_steps = 35
    image_gen_model_id = "stabilityai/stable-diffusion-2"
    image_gen_size = (512, 512)
    image_gen_guidance_scale = 9
    prompt_gen_model_id = "gpt2"
    prompt_dataset_size = 6
    prompt_max_length = 12

secret_hf_token = UserSecretsClient().get_secret("secret_hf_token")
image_gen_model = StableDiffusionPipeline.from_pretrained(
    CFG.image_gen_model_id, torch_dtype=torch.float16,
    revision="fp16", use_auth_token=secret_hf_token, guidance_scale=9
)
image_gen_model = image_gen_model.to(CFG.device)

def generate_image(prompt, model):
    image = model(
        prompt, num_inference_steps=CFG.image_gen_steps,
        generator=CFG.generator,
        guidance_scale=CFG.image_gen_guidance_scale
    ).images[0]
    
    image = image.resize(CFG.image_gen_size)
    return image
generate_image("hyper realistic photo of very friendly and dystopian crater", image_gen_model)

def generate_prompts(model, starting_phrase, max_length, num_return_sequences):
    set_seed(CFG.seed)
    prompts = model(
        starting_phrase, max_length=max_length,
        num_return_sequences=num_return_sequences
    )
    return [prompt["generated_text"] for prompt in prompts]

generated_prompts = generate_prompts(prompts_gen_model, "A picture of ", CFG.prompt_max_length, CFG.prompt_dataset_size)

print(generated_prompts)

def generate_images_by_prompts(prompts, model):
    return [generate_image(prompt, model) for prompt in prompts]

generated_images = generate_images_by_prompts(generated_prompts, image_gen_model)
