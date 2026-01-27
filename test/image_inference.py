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
object_img = Image.open("./test/02015_00.jpg").convert("RGB")

prompt = (
    "A female model from the first image is wearing the dress from the second image, "
    "properly aligned, natural pose, correct body proportions, realistic fabric folds, "
    "photorealistic style, soft lighting"
)

image = pipe(
    prompt=prompt,
    image=[person_img, object_img],  # ✅ 关键点
    height=1024,
    width=1024,
    guidance_scale=1.0,
    num_inference_steps=10,
).images[0]

image.save("composed.png")
