import torch
from diffusers import StableDiffusionPipeline

print("Testing basic imports...")
print("PyTorch version:", torch.__version__)
print("MPS available:", torch.backends.mps.is_available())

try:
    print("Loading Stable Diffusion pipeline...")
    pipeline = StableDiffusionPipeline.from_pretrained(
        "runwayml/stable-diffusion-v1-5",
        torch_dtype=torch.float16
    )
    print("Pipeline loaded successfully!")
    
    # Проверяем устройство
    if torch.backends.mps.is_available():
        device = "mps"
        print("Using MPS")
    else:
        device = "cpu"
        print("Using CPU")
    
    pipeline.to(device)
    
    # Генерируем тестовое изображение
    prompt = "a cute cat"
    print(f"Generating image with prompt: {prompt}")
    
    image = pipeline(prompt).images[0]
    print("Image generated!")
    
    # Сохраняем
    image.save("test_output.png")
    print("Image saved as test_output.png")
    
except Exception as e:
    print(f"Error: {e}")
    print("Trying to import specific components...")
    
    try:
        from diffusers import AutoencoderKL, UNet2DConditionModel
        print("Basic components imported successfully!")
    except Exception as e2:
        print(f"Component import failed: {e2}")
