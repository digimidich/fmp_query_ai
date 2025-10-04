# 🤖 Digimidi Query AI Builder

A web application for querying FileMaker databases using natural language with AI assistance.

## Features

- **Natural Language Queries**: Use plain language to search FileMaker databases
- **AI-Powered**: OpenAI integration for intelligent query processing
- **FileMaker Integration**: Direct connection to FileMaker Script API
- **Clean Interface**: Simple, professional design
- **Sortable Tables**: Interactive data tables with sorting and filtering
- **Age Calculation**: Automatic age calculation from birth dates
- **Responsive Design**: Works on all devices

## Local Development

### Prerequisites
- Node.js 18+ 
- npm

### Installation
```bash
# Install dependencies
npm install

# Start development server
npm start
```

The application will be available at `http://localhost:3000`

## GitLab Setup & Deployment

### Step 1: Create GitLab Project

1. **Create a new GitLab project**
   - Go to [GitLab.com](https://gitlab.com) or your GitLab instance
   - Click "New Project" → "Create blank project"
   - Name: `digimidi-query-builder`
   - Visibility: Private or Public (your choice)
   - Initialize with README: No (we already have files)

2. **Push your code to GitLab**
   ```bash
   # Initialize git repository
   git init
   git add .
   git commit -m "Initial commit: Digimidi Query Builder"
   
   # Add GitLab remote
   git remote add origin https://gitlab.com/your-username/digimidi-query-builder.git
   
   # Push to GitLab
   git push -u origin main
   ```

3. **Configure GitLab CI/CD Variables**
   - Go to your project → Settings → CI/CD → Variables
   - Add these variables:
     - `KOYEB_TOKEN`: Your Koyeb API token
     - `KOYEB_SERVICE_ID`: Your Koyeb service ID
     - `KOYEB_APP_NAME`: Your Koyeb app name

### Step 2: GitLab CI/CD Pipeline

The project includes a complete GitLab CI/CD pipeline (`.gitlab-ci.yml`) that:
- **Builds** Docker image automatically
- **Tests** the application
- **Scans** for security vulnerabilities
- **Deploys** to Koyeb (manual trigger)

### Step 3: Link to Koyeb

Once your GitLab pipeline is running, you can link it to Koyeb:

## Koyeb Deployment

### Method 1: Using Koyeb CLI

1. **Install Koyeb CLI**
   
   **For Linux:**
   ```bash
   # Method 1: Direct download and extract
   curl -L https://github.com/koyeb/koyeb-cli/releases/latest/download/koyeb-cli_linux_amd64.tar.gz | tar -xz
   sudo mv koyeb /usr/local/bin/
   
   # Method 2: Download first, then extract
   wget https://github.com/koyeb/koyeb-cli/releases/latest/download/koyeb-cli_linux_amd64.tar.gz
   tar -xzf koyeb-cli_linux_amd64.tar.gz
   sudo mv koyeb /usr/local/bin/
   ```
   
   **For macOS:**
   ```bash
   # Using Homebrew (recommended)
   brew install koyeb/koyeb/koyeb
   
   # Or manual download
   curl -L https://github.com/koyeb/koyeb-cli/releases/latest/download/koyeb-cli_darwin_amd64.tar.gz | tar -xz
   sudo mv koyeb /usr/local/bin/
   ```
   
   **For Windows:**
   ```powershell
   # Download and extract manually
   Invoke-WebRequest -Uri "https://github.com/koyeb/koyeb-cli/releases/latest/download/koyeb-cli_windows_amd64.zip" -OutFile "koyeb-cli.zip"
   Expand-Archive -Path "koyeb-cli.zip" -DestinationPath "."
   # Move koyeb.exe to your PATH
   ```

2. **Login to Koyeb**
   ```bash
   koyeb auth login
   ```

3. **Deploy the application**
   ```bash
   # Create a new app
   koyeb app create digimidi-query-builder

   # Deploy the service
   koyeb service create digimidi-query-builder \
     --app digimidi-query-builder \
     --dockerfile Dockerfile \
     --ports 3000:http \
     --env NODE_ENV=production \
     --env PORT=3000
   ```

### Method 2: Using Koyeb Dashboard

1. **Create a new app** in the Koyeb dashboard
2. **Connect your Git repository** or upload the files
3. **Configure the service**:
   - **Build Command**: `docker build -t digimidi-query-builder .`
   - **Run Command**: `docker run -p 3000:3000 digimidi-query-builder`
   - **Port**: 3000
   - **Environment Variables**:
     - `NODE_ENV=production`
     - `PORT=3000`

### Method 3: Using Docker

1. **Build the Docker image**
   ```bash
   docker build -t digimidi-query-builder .
   ```

2. **Run locally**
   ```bash
   docker run -p 3000:3000 digimidi-query-builder
   ```

3. **Push to registry** (for Koyeb deployment)
   ```bash
   # Tag for your registry
   docker tag digimidi-query-builder your-registry/digimidi-query-builder:latest
   
   # Push to registry
   docker push your-registry/digimidi-query-builder:latest
   ```

## Configuration

### Environment Variables
- `NODE_ENV`: Set to `production` for production deployment
- `PORT`: Port number (default: 3000)

### FileMaker Configuration
Configure your FileMaker connection in the web interface:
- **Script URL**: Your FileMaker Script API endpoint
- **Credentials**: Username and password
- **Authentication**: Basic auth or Base64 encoded string

### OpenAI Configuration
- **API Key**: Your OpenAI API key
- **Model**: Choose between GPT-4o, GPT-4o Mini, or GPT-3.5 Turbo

## File Structure

```
├── webodata.html          # Main HTML application
├── server.js              # Express server
├── package.json          # Node.js dependencies
├── Dockerfile             # Docker configuration
├── koyeb.yaml            # Koyeb deployment config
└── README.md             # This file
```

## Health Check

The application includes a health check endpoint at `/health` that returns:
```json
{
  "status": "OK",
  "timestamp": "2023-12-01T10:00:00.000Z",
  "service": "Digimidi Query Builder"
}
```

## Security

- **Non-root user**: Docker container runs as non-root user
- **Health checks**: Built-in health monitoring
- **Graceful shutdown**: Proper signal handling
- **Environment isolation**: Production environment variables

## Monitoring

- **Health endpoint**: `/health` for service monitoring
- **Logs**: Available in Koyeb dashboard
- **Metrics**: CPU and memory usage monitoring

## Support

For issues or questions:
1. Check the health endpoint: `https://your-app.koyeb.app/health`
2. Review logs in Koyeb dashboard
3. Verify environment variables are set correctly

## License

MIT License - see LICENSE file for details.
