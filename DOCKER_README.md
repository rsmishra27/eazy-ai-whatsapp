# Docker Deployment Guide

## Quick Start

### 1. Test Docker Build Locally
```bash
# Build and test the Docker image
./deploy.sh build
```

### 2. Test with Docker Compose
```bash
# Start the service with Docker Compose
docker-compose up -d

# Check logs
docker-compose logs -f

# Test health endpoint
curl http://localhost:8000/health

# Stop the service
docker-compose down
```

### 3. Manual Docker Commands
```bash
# Build the image
docker build -t whatsapp-ai-bot .

# Run the container
docker run -p 8000:8000 --env-file .env whatsapp-ai-bot

# Test health endpoint
curl http://localhost:8000/health
```

## What's Included

### Files Created:
- `Dockerfile` - Docker image configuration
- `.dockerignore` - Files to exclude from Docker build
- `docker-compose.yml` - Local development setup
- `deploy.sh` - Deployment helper script
- `main.py` - Updated with health check endpoint

### Features:
- ✅ Python 3.9 slim base image
- ✅ Security: Non-root user
- ✅ Health check endpoint
- ✅ Environment variable support
- ✅ Data volume mounting
- ✅ Optimized for production

## Next Steps

After successful local testing:

1. **AWS ECR Setup** - Push image to Elastic Container Registry
2. **ECS Cluster** - Create Fargate cluster
3. **Load Balancer** - Set up Application Load Balancer
4. **Service Deployment** - Deploy container to ECS

## Troubleshooting

### Common Issues:

1. **Build fails**: Check if all dependencies are in requirements.txt
2. **Container won't start**: Check .env file exists and has correct values
3. **Health check fails**: Wait 30-40 seconds for model loading
4. **Port conflicts**: Make sure port 8000 is not in use

### Debug Commands:
```bash
# Check container logs
docker logs whatsapp-ai-test

# Run container interactively
docker run -it --env-file .env whatsapp-ai-bot /bin/bash

# Check if port is available
lsof -i :8000
```
