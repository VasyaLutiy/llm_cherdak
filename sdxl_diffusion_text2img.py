# Inference
# this is the inference code that you can use after you have trained your model
# Unhide code below and change prj_path to your repo or local path (e.g. my_dreambooth_project)
#
#
#
from diffusers import DiffusionPipeline, StableDiffusionXLImg2ImgPipeline, StableDiffusionPipeline
import torch
from transformers import CLIPTokenizer


model = "stabilityai/stable-diffusion-xl-base-1.0"
#model = "stabilityai/sdxl-turbo"
pipe = DiffusionPipeline.from_pretrained(
    model,
    torch_dtype=torch.float16,
)



pipe.to("cuda")
prj_path = "/home/quit/TF_Projects/gpt/diffusion_torch/my-dreambooth-Capibara-xlbase"
pipe.load_lora_weights(prj_path, weight_name="pytorch_lora_weights.safetensors")

refiner = StableDiffusionXLImg2ImgPipeline.from_pretrained(
    "stabilityai/stable-diffusion-xl-refiner-1.0",
    torch_dtype=torch.float16,
)
refiner.to("cuda")

prompt = """A cinematic digital painting in the style of 'Lucky Capibara'. A Lucky Capibara is in a cathedral with old runes on the walls. In the middle of the cathedral stands a majestic fountain. The camera is located behind the capibara's back and slightly above, showing the capibara character looking at everything around.
"""
# Инициализация токенизатора и тримминг запроса
tokenizer = CLIPTokenizer.from_pretrained("openai/clip-vit-large-patch14")
tokens = tokenizer(prompt, truncation=True, max_length=77, return_tensors="pt")
input_ids = tokens["input_ids"][0][:77]  # Обрезаем токены до 77 длины
trimmed_prompt = tokenizer.decode(input_ids, skip_special_tokens=True)
print(trimmed_prompt)

input_ids = pipe.tokenizer(
    prompt, 
    return_tensors="pt", 
    truncation=False
).input_ids.to("cuda")

seed = 56127
generator = torch.Generator("cuda").manual_seed(seed)
image = pipe(prompt=trimmed_prompt, generator=generator).images[0]
image = refiner(prompt=trimmed_prompt, generator=generator, image=image).images[0]
#image.save(f"/home/quit/TF_Projects/gpt/diffusion_torch/generated_images/generated_image.png")
image
