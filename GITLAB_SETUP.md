# 🚀 GitLab Setup Guide for Digimidi Query Builder

This guide will help you set up a GitLab project with Docker CI/CD pipeline and link it to Koyeb.

## 📋 Prerequisites

- GitLab account (GitLab.com or self-hosted)
- Koyeb account
- Git installed on your local machine

## 🔧 Step 1: Create GitLab Project

### 1.1 Create New Project
1. Go to [GitLab.com](https://gitlab.com) (or your GitLab instance)
2. Click **"New Project"** → **"Create blank project"**
3. Fill in the details:
   - **Project name**: `digimidi-query-builder`
   - **Project slug**: `digimidi-query-builder`
   - **Visibility Level**: Private or Public (your choice)
   - **Initialize repository with a README**: ❌ **Uncheck this**
4. Click **"Create project"**

### 1.2 Get Project URL
After creating the project, you'll see a page with commands. Note the **HTTPS** URL:
```
https://gitlab.com/your-username/digimidi-query-builder.git
```

## 📤 Step 2: Push Code to GitLab

### 2.1 Initialize Local Repository
```bash
# Navigate to your project directory
cd /path/to/your/digimidi-query-builder

# Initialize git repository
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Digimidi Query Builder with Docker CI/CD"
```

### 2.2 Connect to GitLab
```bash
# Add GitLab remote (replace with your actual URL)
git remote add origin https://gitlab.com/digimidi-query-builder/digimidi-query-builder.git

# Push to GitLab
git push -u origin main
```

## ⚙️ Step 3: Configure GitLab CI/CD Variables

### 3.1 Access CI/CD Settings
1. Go to your GitLab project
2. Navigate to **Settings** → **CI/CD**
3. Expand **Variables** section

### 3.2 Add Required Variables
Add these variables (click **"Add variable"** for each):

| Variable | Value | Description |
|----------|-------|-------------|
| `KOYEB_TOKEN` | `your-koyeb-api-token` | Koyeb API token for authentication |
| `KOYEB_SERVICE_ID` | `your-service-id` | Koyeb service ID to update |
| `KOYEB_APP_NAME` | `your-app-name` | Koyeb app name for URL |

### 3.3 Get Koyeb Credentials
To get your Koyeb credentials:

1. **Get Koyeb API Token**:
   ```bash
   # Install Koyeb CLI first
   curl -L https://github.com/koyeb/koyeb-cli/releases/latest/download/koyeb-cli_linux_amd64.tar.gz | tar -xz
   sudo mv koyeb /usr/local/bin/
   
   # Login and get token
   koyeb auth login
   ```

2. **Get Service ID**:
   ```bash
   # List your services
   koyeb service list
   ```

3. **Get App Name**:
   ```bash
   # List your apps
   koyeb app list
   ```

## 🐳 Step 4: GitLab CI/CD Pipeline

### 4.1 Pipeline Overview
The `.gitlab-ci.yml` file includes:

- **Build Stage**: Creates Docker image and pushes to GitLab Container Registry
- **Test Stage**: Runs syntax checks and basic tests
- **Security Stage**: Scans Docker image for vulnerabilities
- **Deploy Stage**: Deploys to Koyeb (manual trigger)

### 4.2 Pipeline Stages
```yaml
stages:
  - build    # Build Docker image
  - test     # Run tests
  - deploy   # Deploy to Koyeb
```

### 4.3 Manual Deployment
The deployment to Koyeb is **manual** for safety:
1. Go to **CI/CD** → **Pipelines**
2. Find your pipeline
3. Click **"Deploy to Koyeb"** button
4. Monitor the deployment

## 🔗 Step 5: Link to Koyeb

### 5.1 Create Koyeb App
```bash
# Create Koyeb app
koyeb app create digimidi-query-builder

# Create service
koyeb service create digimidi-query-builder \
  --app digimidi-query-builder \
  --dockerfile Dockerfile \
  --ports 3000:http \
  --env NODE_ENV=production \
  --env PORT=3000
```

### 5.2 Configure GitLab Integration
1. In Koyeb dashboard, go to your app
2. Navigate to **Settings** → **Git Integration**
3. Connect your GitLab repository
4. Configure auto-deploy settings

## 🚀 Step 6: Deploy and Test

### 6.1 Trigger Pipeline
```bash
# Make a small change to trigger pipeline
echo "# Updated $(date)" >> README.md
git add README.md
git commit -m "Trigger CI/CD pipeline"
git push origin main
```

### 6.2 Monitor Deployment
1. Go to **CI/CD** → **Pipelines** in GitLab
2. Watch the pipeline progress
3. Check logs for any errors
4. Verify deployment in Koyeb dashboard

### 6.3 Test Application
Once deployed, test your application:
```bash
# Get your app URL
koyeb app get digimidi-query-builder

# Test health endpoint
curl https://your-app.koyeb.app/health
```

## 🔧 Troubleshooting

### Common Issues

1. **Pipeline Fails on Build**:
   - Check Dockerfile syntax
   - Verify all files are committed
   - Check GitLab Container Registry permissions

2. **Deployment Fails**:
   - Verify Koyeb credentials
   - Check service ID is correct
   - Ensure Koyeb service exists

3. **Permission Denied**:
   - Check GitLab CI/CD variables are set
   - Verify Koyeb token has correct permissions
   - Ensure service ID is accessible

### Debug Commands
```bash
# Check GitLab CI/CD logs
gitlab-ci-multi-runner exec docker build

# Test Docker build locally
docker build -t digimidi-query-builder .

# Test Koyeb CLI
koyeb service list
koyeb app list
```

## 📊 Monitoring

### GitLab CI/CD
- **Pipelines**: Monitor build status
- **Jobs**: Check individual job logs
- **Variables**: Verify environment variables

### Koyeb Dashboard
- **Services**: Monitor service health
- **Logs**: View application logs
- **Metrics**: CPU, memory, and network usage

## 🎯 Next Steps

1. **Set up monitoring**: Configure alerts for failed deployments
2. **Add tests**: Expand test coverage in CI/CD pipeline
3. **Security**: Enable security scanning and dependency checks
4. **Scaling**: Configure auto-scaling in Koyeb
5. **Backup**: Set up database backups if needed

## 📚 Resources

- [GitLab CI/CD Documentation](https://docs.gitlab.com/ee/ci/)
- [Koyeb Documentation](https://www.koyeb.com/docs)
- [Docker Documentation](https://docs.docker.com/)
- [Node.js Best Practices](https://github.com/goldbergyoni/nodebestpractices)

---

**Need help?** Check the troubleshooting section or create an issue in your GitLab project.
