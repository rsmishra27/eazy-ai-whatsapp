#!/bin/bash

# WhatsApp AI Bot Deployment Script
set -e

echo "🚀 Starting WhatsApp AI Bot Deployment..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found. Please create it with required environment variables."
    exit 1
fi

# Function to build and test Docker image
build_and_test() {
    echo "📦 Building Docker image..."
    docker build -t whatsapp-ai-bot .
    
    echo "🧪 Testing Docker image locally..."
    docker run -d --name whatsapp-ai-test -p 8000:8000 --env-file .env whatsapp-ai-bot
    
    # Wait for container to start (ML models need more time)
    echo "⏳ Waiting for container to start (ML models loading)..."
    sleep 60
    
    # Test health endpoint with retries
    echo "🔍 Testing health endpoint..."
    for i in {1..5}; do
        echo "Attempt $i/5..."
        if curl -f http://localhost:8000/health; then
            echo "✅ Health check passed!"
            break
        else
            echo "⏳ Still loading... waiting 10 more seconds"
            sleep 10
        fi
        
        if [ $i -eq 5 ]; then
            echo "❌ Health check failed after 5 attempts!"
            echo "📋 Container logs:"
            docker logs whatsapp-ai-test
            docker stop whatsapp-ai-test
            docker rm whatsapp-ai-test
            exit 1
        fi
    done
    
    # Clean up test container
    docker stop whatsapp-ai-test
    docker rm whatsapp-ai-test
    echo "✅ Local test completed successfully!"
}

# Function to show next steps
show_next_steps() {
    echo ""
    echo "🎉 Docker setup completed successfully!"
    echo ""
    echo "Next steps for AWS ECS deployment:"
    echo "1. Install AWS CLI: https://aws.amazon.com/cli/"
    echo "2. Configure AWS credentials: aws configure"
    echo "3. Create ECR repository:"
    echo "   aws ecr create-repository --repository-name whatsapp-ai-bot"
    echo "4. Get ECR login command:"
    echo "   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com"
    echo "5. Tag and push image:"
    echo "   docker tag whatsapp-ai-bot:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/whatsapp-ai-bot:latest"
    echo "   docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/whatsapp-ai-bot:latest"
    echo ""
    echo "Or use Docker Compose for local testing:"
    echo "   docker-compose up -d"
    echo ""
}

# Main execution
case "${1:-build}" in
    "build")
        build_and_test
        show_next_steps
        ;;
    "test")
        echo "🧪 Testing existing Docker image..."
        docker run -d --name whatsapp-ai-test -p 8000:8000 --env-file .env whatsapp-ai-bot
        sleep 10
        curl -f http://localhost:8000/health
        docker stop whatsapp-ai-test
        docker rm whatsapp-ai-test
        echo "✅ Test completed!"
        ;;
    "clean")
        echo "🧹 Cleaning up Docker resources..."
        docker stop whatsapp-ai-test 2>/dev/null || true
        docker rm whatsapp-ai-test 2>/dev/null || true
        docker rmi whatsapp-ai-bot 2>/dev/null || true
        echo "✅ Cleanup completed!"
        ;;
    *)
        echo "Usage: $0 [build|test|clean]"
        echo "  build: Build and test Docker image (default)"
        echo "  test:  Test existing Docker image"
        echo "  clean: Clean up Docker resources"
        exit 1
        ;;
esac
