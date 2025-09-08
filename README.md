# 🤖 WhatsApp AI Shopping Assistant

A powerful WhatsApp chatbot that provides intelligent product recommendations using AI and vector search. The bot can handle 20,000+ products loaded from S3 and provides personalized shopping assistance.

## ✨ Features

- **WhatsApp Integration** - Direct messaging through Twilio
- **AI-Powered Search** - Semantic product search using FAISS vector database
- **S3 Product Storage** - Loads products from AWS S3 (supports 20k+ products)
- **Multilingual Support** - English and Arabic language support
- **Voice Message Support** - Transcribes audio messages using AssemblyAI
- **Docker Containerized** - Easy deployment and scaling
- **Lazy Loading** - Fast startup with on-demand model loading
- **Product Recommendations** - Returns products with prices, descriptions, and affiliate links

## 🏗️ Architecture

- **FastAPI** - Web framework for API endpoints
- **LangGraph** - AI workflow orchestration
- **FAISS** - Vector similarity search
- **S3** - Product data storage
- **Docker** - Containerization
- **Twilio** - WhatsApp messaging
- **AssemblyAI** - Voice transcription
- **Google Gemini** - AI language model

## 📋 Prerequisites

- Docker and Docker Compose
- AWS CLI configured with S3 access
- Twilio account with WhatsApp Sandbox
- Google Gemini API key
- AssemblyAI API key (optional)

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone <repository-url>
cd eazy-ai-whatsapp
```

### 2. Set Up Environment Variables
```bash
# Copy the template
cp .env.template .env

# Edit with your credentials
nano .env
```

Required environment variables:
```bash
# Twilio Configuration
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886

# AI APIs
GEMINI_API_KEY=your_gemini_api_key
ASSEMBLYAI_API_KEY=your_assemblyai_api_key

# AWS Credentials (for S3 access)
AWS_ACCESS_KEY_ID=your_aws_access_key_id
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
AWS_DEFAULT_REGION=us-east-1
```

### 3. Set Up AWS Credentials
```bash
# Option 1: Use AWS CLI (recommended)
aws configure

# Option 2: Add to .env file
echo "AWS_ACCESS_KEY_ID=$(aws configure get aws_access_key_id)" >> .env
echo "AWS_SECRET_ACCESS_KEY=$(aws configure get aws_secret_access_key)" >> .env
echo "AWS_DEFAULT_REGION=$(aws configure get region)" >> .env
```

### 4. Create Data Directory
```bash
mkdir -p data
```

### 5. Run with Docker Compose
```bash
# Build and start the container
docker-compose up --build -d

# Check if it's running
docker-compose ps

# View logs
docker-compose logs -f
```

### 6. Test the Application
```bash
# Test health endpoint
curl http://localhost:8000/health

# Test webhook endpoint
curl -X POST http://localhost:8000/webhook \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "From=whatsapp:+1234567890&Body=Hi"

# Test product search
curl -X POST http://localhost:8000/webhook \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "From=whatsapp:+1234567890&Body=Show me shoes under 200 AED"
```

## 📱 WhatsApp Setup

### 1. Set Up Twilio WhatsApp Sandbox
1. Go to [Twilio Console](https://console.twilio.com/)
2. Navigate to **Messaging > Try it out > Send a WhatsApp message**
3. Follow the setup instructions to connect your phone number
4. Note down your sandbox number (usually `+14155238886`)

### 2. Set Up ngrok for Local Testing
```bash
# Install ngrok
brew install ngrok  # macOS
# or download from https://ngrok.com/

# Expose your local server
ngrok http 8000
```

### 3. Configure Twilio Webhook
1. Copy your ngrok URL (e.g., `https://abc123.ngrok-free.app`)
2. Go to Twilio Console > Phone Numbers > Manage > Active Numbers
3. Click on your WhatsApp sandbox number
4. Set webhook URL to: `https://your-ngrok-url.ngrok-free.app/webhook`
5. Set HTTP method to `POST`

### 4. Test with WhatsApp
1. Send a message to your Twilio sandbox number
2. The chatbot will respond with product recommendations

## 🛍️ Product Data Setup

### S3 Structure
The bot expects product data in S3 with the following structure:
```
s3://your-bucket/products/
├── products_1.csv
├── products_2.csv
└── ...
```

### CSV Format
Each CSV file should contain products with these columns:
- `title` - Product name
- `description` - Product description
- `price` - Product price
- `currency` - Currency (e.g., AED, USD)
- `category` - Product category
- `brand` - Product brand
- `affiliate_url` - Product link
- `image_url` - Product image URL

### Update S3 Configuration
Edit `app/core/s3_loader.py` to match your S3 bucket:
```python
self.bucket_name = 'your-bucket-name'
self.prefix = 'products/'  # Adjust as needed
```

## 🔧 Development

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
python main.py
```

### Docker Development
```bash
# Build image
docker build -t whatsapp-ai-bot .

# Run container
docker run -d --name whatsapp-ai-bot \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  --env-file .env \
  whatsapp-ai-bot
```

### View Logs
```bash
# Docker Compose
docker-compose logs -f

# Docker
docker logs -f whatsapp-ai-bot
```

## 📊 Performance

### First Startup
- **Loading 20k products**: 2-3 minutes
- **Building FAISS index**: 1-2 minutes
- **Total startup time**: 3-5 minutes

### Subsequent Startups
- **Loading from cache**: 10-30 seconds
- **Total startup time**: 30-60 seconds

### Memory Usage
- **Container memory**: ~2-4 GB
- **FAISS index size**: ~50-100 MB
- **Product data**: ~10-20 MB

## 🚀 Deployment

### AWS ECS Deployment
1. **Build and push to ECR**:
   ```bash
   aws ecr create-repository --repository-name whatsapp-ai-bot
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
   docker tag whatsapp-ai-bot:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/whatsapp-ai-bot:latest
   docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/whatsapp-ai-bot:latest
   ```

2. **Create ECS cluster and service**
3. **Set up Application Load Balancer**
4. **Configure environment variables**

### Docker Compose Production
```bash
# Production docker-compose.yml
version: '3.8'
services:
  whatsapp-ai-bot:
    image: your-registry/whatsapp-ai-bot:latest
    ports:
      - "8000:8000"
    environment:
      - TWILIO_ACCOUNT_SID=${TWILIO_ACCOUNT_SID}
      - TWILIO_AUTH_TOKEN=${TWILIO_AUTH_TOKEN}
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
    volumes:
      - ./data:/app/data
    restart: unless-stopped
```

## 🔍 Troubleshooting

### Common Issues

1. **Container won't start**:
   ```bash
   # Check logs
   docker-compose logs whatsapp-ai-bot
   
   # Check environment variables
   docker-compose config
   ```

2. **AWS credentials error**:
   ```bash
   # Verify AWS credentials
   aws sts get-caller-identity
   
   # Check .env file
   cat .env | grep AWS
   ```

3. **S3 access denied**:
   ```bash
   # Test S3 access
   aws s3 ls s3://your-bucket/products/
   
   # Check IAM permissions
   aws iam get-user
   ```

4. **Webhook not working**:
   ```bash
   # Test webhook directly
   curl -X POST http://localhost:8000/webhook \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "From=whatsapp:+1234567890&Body=test"
   
   # Check ngrok status
   curl http://127.0.0.1:4040/api/tunnels
   ```

5. **Health check fails**:
   ```bash
   # Check container status
   docker ps -a
   
   # Check health endpoint
   curl http://localhost:8000/health
   ```

### Debug Commands
```bash
# Run container interactively
docker run -it --env-file .env whatsapp-ai-bot /bin/bash

# Check container resources
docker stats whatsapp-ai-bot

# View detailed logs
docker logs --details whatsapp-ai-bot
```

## 📈 Monitoring

### Health Checks
- **Endpoint**: `GET /health`
- **Response**: `{"status": "healthy", "service": "whatsapp-ai-agent", "models": "ready"}`

### Logs
- **Application logs**: Container stdout
- **Error logs**: Container stderr
- **Access logs**: HTTP request logs

### Metrics
- **Response time**: API endpoint performance
- **Memory usage**: Container resource usage
- **Product search**: Search query performance

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review the logs for error details

## 🎯 Demo Scenarios

### Basic Chat
- **User**: "Hi"
- **Bot**: "Hello! I'm your shopping assistant. How can I help you today?"

### Product Search
- **User**: "Show me shoes under 200 AED"
- **Bot**: Returns 5 shoes with prices, descriptions, and affiliate links

### Voice Messages
- **User**: Sends voice message
- **Bot**: Transcribes and responds with product recommendations

---

**Happy Shopping! 🛍️**