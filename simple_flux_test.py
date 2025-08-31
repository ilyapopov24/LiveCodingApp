import torch
from PIL import Image
import numpy as np

print("PyTorch version:", torch.__version__)
print("MPS available:", torch.backends.mps.is_available())

# Создаем простое тестовое изображение
print("Creating test image...")
test_image = np.random.randint(0, 255, (512, 512, 3), dtype=np.uint8)
image = Image.fromarray(test_image)
image.save("test_input.png")
print("Test image saved as test_input.png")

# Проверяем устройство
if torch.backends.mps.is_available():
    device = "mps"
    print("Using MPS")
else:
    device = "cpu"
    print("Using CPU")

# Создаем простую модель для демонстрации
print("Creating simple model...")
model = torch.nn.Sequential(
    torch.nn.Conv2d(3, 64, 3, padding=1),
    torch.nn.ReLU(),
    torch.nn.Conv2d(64, 3, 3, padding=1)
).to(device)

print("Model created successfully!")

# Тестируем forward pass
print("Testing model...")
test_tensor = torch.randn(1, 3, 512, 512).to(device)
with torch.no_grad():
    output = model(test_tensor)
    print(f"Model output shape: {output.shape}")

print("All tests passed!")
print("Ready for FLUX model integration!")
