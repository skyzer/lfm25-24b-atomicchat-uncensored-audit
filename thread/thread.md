# Thread

### Post 1/8 (256 chars, image: img/post_01.png)

On Oct 14 AtomicChat posted about their uncensored LFM2.5-24B-A2B GGUF:

"We cut refusals from 96% to 1% and improved the model's accuracy … 65.6% of MMLU questions right vs 64.4% for the original"

I checked the weights, the behaviour and both numbers 🧵

### Post 2/8 (267 chars, image: img/post_02.png)

1. Card vs file
• The card says it's an abliteration: a refusal direction removed from 52 matrices in blocks 14–39, scale 1.75
• The GGUF metadata says the same, and names their published directions file by hash
• Tokenizer and chat template: identical to Liquid's

### Post 3/8 (261 chars, image: img/post_03.png)

2. Weight diff vs a clean control
• I compressed Liquid's BF16 to Q8_0 myself. Q8_0/F16/F32 are deterministic, so untouched tensors must match byte for byte
• 376 of 428 do. The 52 that don't are exactly the card's list
• Their plain build: 428/428 identical

### Post 4/8 (254 chars, image: img/post_04.png)

3. Shape of the edit
• Each of the 52 changes is rank-1 along their published direction (|cos| ≥ 0.99999)
• The fitted strength is −0.75, i.e. 1 − 1.75, as the card says
• Their LoRA is the same edit, factored

No evidence found of any other change

### Post 5/8 (239 chars, image: img/post_05.png)

4. Behaviour, with the network cut and strace on
• 0 outbound connection attempts
• 50 trigger prefixes × 10 prompts, incl. their own name: largest shift 2.99 SD, none above 3
• 70 agent tasks: 0 flagged tool calls, 0 unexpected domains

### Post 6/8 (244 chars, image: img/post_06.png)

5. Refusals, Liquid → Uncensored, same Q5 quant and harness
• 20 harmful, no think: 20/20 → 0/20
• Same, think on: 20/20 → 2/20
• JBB-100: 95/100 → 0/100 (think: 93/100 → 13/100)
• XSTest safe: 39/250 → 0/250
The refusal drop holds up

### Post 7/8 (277 chars, image: img/post_07.png)

6. MMLU
• Liquid publishes no score. AtomicChat's 64.4% is an unpublished 2,000-q subset that also picked the variant
• Mine, Q5, 3,000 paired Qs: 58.6% → 65.2%, +6.6 pts (CI +5.0 to +8.3)
• Liquid often runs past the answer cap. Where both answered: +2.7 (CI +1.1 to +4.4)

### Post 8/8 (276 chars, image: img/post_08.png)

Verdict
• A rank-1 abliteration, as the card says. No evidence found of anything else
• Refusals: big drop, confirmed
• "Improved accuracy": small gain at Q5, partly format
Limits: one quant, regex refusal count, 3k MMLU Qs, 0-shot
Scripts + hashes: REPO_URL
