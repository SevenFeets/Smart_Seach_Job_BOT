# Ollama Setup Guide

This guide covers all options for using Ollama with the LinkedIn Job Bot.

## Option 1: Local Ollama (Completely Free)

### Windows Installation

```powershell
# Download and install from https://ollama.ai/download
# Or use winget:
winget install Ollama.Ollama

# Pull a model
ollama pull llama2

# Start the server (runs in background)
ollama serve
```

### Configuration

```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
```

**Pros:**
- ✅ Completely free
- ✅ No API limits
- ✅ Privacy (runs locally)

**Cons:**
- ❌ Requires local resources (RAM, CPU/GPU)
- ❌ Server must be running

---

## Option 2: Remote Ollama Server

You can host Ollama on a remote server and access it via API.

### Self-Hosted on Cloud

#### Deploy on DigitalOcean/AWS/GCP

```bash
# On your cloud server (Ubuntu example)
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull llama2
ollama serve

# Expose the service (use nginx for HTTPS)
# Configure firewall to allow port 11434
```

#### Configuration

```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=https://your-server-ip:11434
# Or with domain:
OLLAMA_BASE_URL=https://ollama.yourdomain.com
OLLAMA_MODEL=llama2
```

**Pros:**
- ✅ No local resources needed
- ✅ Can use powerful cloud GPUs
- ✅ Always available

**Cons:**
- ❌ Cloud hosting costs
- ❌ Requires server setup

---

## Option 3: Replicate (Ollama-Compatible)

Replicate offers Ollama models with pay-per-use pricing.

### Setup

1. Sign up at [replicate.com](https://replicate.com)
2. Get your API token
3. Find an Ollama-compatible model

### Configuration

While Replicate doesn't use the exact Ollama API, you can modify the code to use it:

```env
# Use the custom provider option
LLM_PROVIDER=groq  # Or create a custom replicate provider
# See src/ai/cover_letter.py for implementation
```

---

## Option 4: Third-Party Ollama Hosting

Several services offer hosted Ollama:

### Popular Options

1. **RunPod** - GPU cloud hosting
   - URL: https://www.runpod.io
   - Can deploy Ollama containers
   - Pay per hour

2. **Modal** - Serverless GPU
   - URL: https://modal.com
   - Good for intermittent use
   - Pay per invocation

3. **Banana.dev** - ML hosting
   - URL: https://www.banana.dev
   - Specialized for ML models

### General Configuration

```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=https://your-hosted-endpoint.com
OLLAMA_MODEL=llama2
OLLAMA_API_KEY=your_api_key  # If the service requires authentication
```

---

## Recommended Models

Different models for different use cases:

### Fast & Lightweight
```env
OLLAMA_MODEL=llama2  # 7B params, good balance
```

### Better Quality
```env
OLLAMA_MODEL=mistral  # Often better than llama2
OLLAMA_MODEL=mixtral  # Large, high quality
```

### Specialized for Writing
```env
OLLAMA_MODEL=neural-chat  # Good for conversational text
```

### List Available Models

```bash
ollama list
```

---

## Ollama API with Authentication

If your Ollama server requires authentication, the bot now supports API keys:

```env
OLLAMA_BASE_URL=https://secure-ollama.example.com
OLLAMA_MODEL=llama2
OLLAMA_API_KEY=your_secure_api_key
```

The API key will be sent as a Bearer token in the Authorization header.

---

## Testing Your Setup

Test if Ollama is accessible:

```powershell
# Test local Ollama
curl http://localhost:11434/api/generate -d '{
  "model": "llama2",
  "prompt": "Write a short greeting",
  "stream": false
}'

# Test remote Ollama
curl https://your-server.com/api/generate -H "Authorization: Bearer YOUR_KEY" -d '{
  "model": "llama2",
  "prompt": "Write a short greeting",
  "stream": false
}'
```

Or test with the bot:

```powershell
# Create a simple test
python -c "
import asyncio
from src.ai.cover_letter import CoverLetterGenerator

async def test():
    gen = CoverLetterGenerator()
    result = await gen.generate(
        job_title='Software Engineer',
        company='Test Company',
        job_description='Test job'
    )
    print(result)

asyncio.run(test())
"
```

---

## Troubleshooting

### Connection Refused
```
Error: Could not connect to Ollama
```

**Solutions:**
- Check if Ollama is running: `ollama list`
- Verify URL in .env
- Check firewall settings
- For remote: ensure port 11434 is open

### Authentication Error
```
Error: 401 Unauthorized
```

**Solutions:**
- Verify OLLAMA_API_KEY is correct
- Check if server requires authentication
- Ensure Bearer token format is supported

### Model Not Found
```
Error: model 'xxx' not found
```

**Solutions:**
- Pull the model: `ollama pull llama2`
- Check available models: `ollama list`
- Verify OLLAMA_MODEL name in .env

### Slow Response
**Solutions:**
- Use a smaller model (llama2 instead of llama2:70b)
- Reduce `num_predict` in cover_letter.py
- Use GPU-accelerated hosting

---

## Cost Comparison

| Option | Cost | Speed | Quality | Privacy |
|--------|------|-------|---------|---------|
| Local Ollama | Free | Medium | Good | Excellent |
| Cloud Self-Host | $5-50/mo | Fast | Good | Good |
| Replicate | $0.0002/token | Fast | Excellent | Medium |
| Groq (Alternative) | Free tier | Very Fast | Excellent | Medium |

---

## Alternative: Use Groq Instead

If Ollama setup is too complex, Groq offers free API access:

```env
LLM_PROVIDER=groq
GROQ_API_KEY=gsk_your_key_from_console.groq.com
```

Groq is often faster and easier to set up than remote Ollama.
