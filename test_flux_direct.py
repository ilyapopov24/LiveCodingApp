from diffusers import StableDiffusionPipeline
import torch

print("Loading FLUX.1-dev base model...")

# Проверяем доступные устройства
if torch.backends.mps.is_available():
    device = "mps"
    print("Using MPS (Metal Performance Shaders) for acceleration")
elif torch.cuda.is_available():
    device = "cuda"
    print("Using CUDA")
else:
    device = "cpu"
    print("Using CPU")

# Загружаем базовую модель FLUX.1-dev
print("Loading base model...")
pipeline = StableDiffusionPipeline.from_pretrained(
    "black-forest-labs/FLUX.1-dev", 
    torch_dtype=torch.float16,
    use_safetensors=True
).to(device)

print("Base model loaded!")

# Загружаем LoRA веса enhanceaiteam/Flux-uncensored-v2
print("Loading LoRA weights...")
pipeline.load_lora_weights('enhanceaiteam/Flux-uncensored-v2', weight_name='lora.safetensors')
print("LoRA weights loaded!")

# Генерируем изображение
prompt = "a cute girl with purple hair, anime style"
print(f"Generating image with prompt: {prompt}")

image = pipeline(prompt).images[0]
print("Image generated successfully!")

# Сохраняем изображение
output_path = "flux_uncensored_output.png"
image.save(output_path)
print(f"Image saved at: {output_path}")
print("Done!")
