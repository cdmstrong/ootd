from PIL import Image
import torch
from diffusers import Flux2KleinPipeline

device = "cuda"
dtype = torch.bfloat16

pipe = Flux2KleinPipeline.from_pretrained(
    "./flux2-klein/FLUX.2-klein-4B",
    torch_dtype=dtype,
)
pipe.to(device)

person_img = Image.open("./test/hero2.jpg").convert("RGB")
object_img = Image.open("./test/cat_window.png").convert("RGB")
bird_img = Image.open("./test/bird.png").convert("RGB")

prompt = "The person from image 1 is petting the cat from image 2, the bird from image 3 is next to them"

image = pipe(
    prompt=prompt,
    image=[person_img, object_img, bird_img],  # ✅ 关键点
    height=1024,
    width=1024,
    guidance_scale=1.0,
    num_inference_steps=10,
).images[0]

image.save("composed.png")
