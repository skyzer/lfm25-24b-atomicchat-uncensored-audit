2. Weight diff vs a clean control
• I compressed Liquid's BF16 to Q8_0 myself. Q8_0/F16/F32 are deterministic, so untouched tensors must match byte for byte
• 376 of 428 do. The 52 that don't are exactly the card's list
• Their plain build: 428/428 identical
