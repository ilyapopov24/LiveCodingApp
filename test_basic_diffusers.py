import torch
print("PyTorch version:", torch.__version__)
print("MPS available:", torch.backends.mps.is_available())

try:
    print("Testing basic diffusers imports...")
    from diffusers import AutoencoderKL, UNet2DConditionModel
    print("Basic components imported successfully!")
    
    # Создаем простую модель
    print("Creating simple model...")
    model = AutoencoderKL(
        in_channels=3,
        out_channels=3,
        down_block_types=["DownEncoderBlock2D"],
        up_block_types=["UpDecoderBlock2D"],
        block_out_channels=[64],
        layers_per_block=1,
        act_fn="silu"
    )
    print("Model created successfully!")
    
    # Тестируем на устройстве
    if torch.backends.mps.is_available():
        device = "mps"
        print("Using MPS")
    else:
        device = "cpu"
        print("Using CPU")
    
    model.to(device)
    print("Model moved to device successfully!")
    
    # Тестируем forward pass
    test_input = torch.randn(1, 3, 64, 64).to(device)
    with torch.no_grad():
        output = model(test_input)
        print(f"Forward pass successful! Output shape: {output.sample.shape}")
    
    print("All tests passed!")
    
except Exception as e:
    print(f"Error: {e}")
    print("Trying to import specific components...")
    
    try:
        from diffusers.models import AutoencoderKL
        print("AutoencoderKL imported successfully!")
    except Exception as e2:
        print(f"AutoencoderKL import failed: {e2}")
        
    try:
        from diffusers.models import UNet2DConditionModel
        print("UNet2DConditionModel imported successfully!")
    except Exception as e3:
        print(f"UNet2DConditionModel import failed: {e3}")
