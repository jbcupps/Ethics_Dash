# Deployment Guide

This document outlines the steps to deploy the Ethics Dashboard application using Docker Compose.

## Prerequisites

- Docker installed
- Docker Compose installed
- Access to required API keys (OpenAI, Anthropic, Google)

## Environment Setup

1. Clone the repository to your deployment environment
2. Copy the environment template files:
   ```bash
   cp .env.example .env
   ```
3. Edit the `.env` file with your configuration:
   - API keys for LLM services
   - Environment settings
   - Logging configuration

## Building and Deploying

1. Build all services:
   ```bash
   docker compose build
   ```

2. Start the application stack:
   ```bash
   docker compose up -d
   ```

3. Verify services are running:
   ```bash
   docker compose ps
   ```

4. Check service logs:
   ```bash
   # View all logs
   docker compose logs

   # View specific service logs
   docker compose logs ai-backend
   docker compose logs app
   docker compose logs ai-frontend
   ```

## Service Architecture

The application consists of several Docker containers working together:

- **app** (port 8050): Main Dash application
- **ai-backend** (port 5000): AI/LLM processing backend
- **ai-frontend** (port 80): React frontend served by Nginx
- **ai-mongo** (port 27018): MongoDB database
- **db-init**: One-time database initialization service

## Data Persistence

MongoDB data is persisted using a named Docker volume `mongo_data`. This ensures your data survives container restarts.

## Maintenance

### Updating the Application

1. Pull latest changes:
   ```bash
   git pull
   ```

2. Rebuild and restart services:
   ```bash
   docker compose down
   docker compose build
   docker compose up -d
   ```

### Backup and Restore

1. Backup MongoDB data:
   ```bash
   docker compose exec ai-mongo mongodump --out /data/backup
   ```

2. Restore from backup:
   ```bash
   docker compose exec ai-mongo mongorestore /data/backup
   ```

## Troubleshooting

### Common Issues

1. **Services won't start**
   - Check logs: `docker compose logs`
   - Verify environment variables in `.env`
   - Ensure all required ports are available

2. **Database initialization fails**
   - Check db-init service logs: `docker compose logs db-init`
   - Verify MongoDB connection string
   - Check permissions on mounted volumes

3. **API errors**
   - Verify API keys in environment files
   - Check backend logs: `docker compose logs ai-backend`
   - Ensure services can communicate (check Docker network)

### Health Checks

The services include health checks that can be monitored:

```bash
# Check service health
docker compose ps
```

## Security Notes

1. Never commit `.env` files containing real credentials
2. Regularly update base images and dependencies
3. Follow principle of least privilege for service access
4. Monitor container logs for suspicious activity
5. Keep API keys secure and rotate them regularly

## Scaling Considerations

For higher load scenarios:

1. Increase MongoDB resources
2. Add more backend instances
3. Consider using a reverse proxy for load balancing
4. Monitor resource usage and adjust container limits

## Support

For issues or questions:
1. Check the troubleshooting guide above
2. Review service logs
3. Consult the project documentation
4. Open an issue in the project repository 