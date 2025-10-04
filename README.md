<<<<<<< HEAD
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
=======
# Fmp Query Ai



## Getting started

To make it easy for you to get started with GitLab, here's a list of recommended next steps.

Already a pro? Just edit this README.md and make it your own. Want to make it easy? [Use the template at the bottom](#editing-this-readme)!

## Add your files

- [ ] [Create](https://docs.gitlab.com/ee/user/project/repository/web_editor.html#create-a-file) or [upload](https://docs.gitlab.com/ee/user/project/repository/web_editor.html#upload-a-file) files
- [ ] [Add files using the command line](https://docs.gitlab.com/topics/git/add_files/#add-files-to-a-git-repository) or push an existing Git repository with the following command:

```
cd existing_repo
git remote add origin https://gitlab.com/digimidi/fmp_query_ai.git
git branch -M main
git push -uf origin main
```

## Integrate with your tools

- [ ] [Set up project integrations](https://gitlab.com/digimidi/fmp_query_ai/-/settings/integrations)

## Collaborate with your team

- [ ] [Invite team members and collaborators](https://docs.gitlab.com/ee/user/project/members/)
- [ ] [Create a new merge request](https://docs.gitlab.com/ee/user/project/merge_requests/creating_merge_requests.html)
- [ ] [Automatically close issues from merge requests](https://docs.gitlab.com/ee/user/project/issues/managing_issues.html#closing-issues-automatically)
- [ ] [Enable merge request approvals](https://docs.gitlab.com/ee/user/project/merge_requests/approvals/)
- [ ] [Set auto-merge](https://docs.gitlab.com/user/project/merge_requests/auto_merge/)

## Test and Deploy

Use the built-in continuous integration in GitLab.

- [ ] [Get started with GitLab CI/CD](https://docs.gitlab.com/ee/ci/quick_start/)
- [ ] [Analyze your code for known vulnerabilities with Static Application Security Testing (SAST)](https://docs.gitlab.com/ee/user/application_security/sast/)
- [ ] [Deploy to Kubernetes, Amazon EC2, or Amazon ECS using Auto Deploy](https://docs.gitlab.com/ee/topics/autodevops/requirements.html)
- [ ] [Use pull-based deployments for improved Kubernetes management](https://docs.gitlab.com/ee/user/clusters/agent/)
- [ ] [Set up protected environments](https://docs.gitlab.com/ee/ci/environments/protected_environments.html)

***

# Editing this README

When you're ready to make this README your own, just edit this file and use the handy template below (or feel free to structure it however you want - this is just a starting point!). Thanks to [makeareadme.com](https://www.makeareadme.com/) for this template.

## Suggestions for a good README

Every project is different, so consider which of these sections apply to yours. The sections used in the template are suggestions for most open source projects. Also keep in mind that while a README can be too long and detailed, too long is better than too short. If you think your README is too long, consider utilizing another form of documentation rather than cutting out information.

## Name
Choose a self-explaining name for your project.

## Description
Let people know what your project can do specifically. Provide context and add a link to any reference visitors might be unfamiliar with. A list of Features or a Background subsection can also be added here. If there are alternatives to your project, this is a good place to list differentiating factors.

## Badges
On some READMEs, you may see small images that convey metadata, such as whether or not all the tests are passing for the project. You can use Shields to add some to your README. Many services also have instructions for adding a badge.

## Visuals
Depending on what you are making, it can be a good idea to include screenshots or even a video (you'll frequently see GIFs rather than actual videos). Tools like ttygif can help, but check out Asciinema for a more sophisticated method.

## Installation
Within a particular ecosystem, there may be a common way of installing things, such as using Yarn, NuGet, or Homebrew. However, consider the possibility that whoever is reading your README is a novice and would like more guidance. Listing specific steps helps remove ambiguity and gets people to using your project as quickly as possible. If it only runs in a specific context like a particular programming language version or operating system or has dependencies that have to be installed manually, also add a Requirements subsection.

## Usage
Use examples liberally, and show the expected output if you can. It's helpful to have inline the smallest example of usage that you can demonstrate, while providing links to more sophisticated examples if they are too long to reasonably include in the README.

## Support
Tell people where they can go to for help. It can be any combination of an issue tracker, a chat room, an email address, etc.

## Roadmap
If you have ideas for releases in the future, it is a good idea to list them in the README.

## Contributing
State if you are open to contributions and what your requirements are for accepting them.

For people who want to make changes to your project, it's helpful to have some documentation on how to get started. Perhaps there is a script that they should run or some environment variables that they need to set. Make these steps explicit. These instructions could also be useful to your future self.

You can also document commands to lint the code or run tests. These steps help to ensure high code quality and reduce the likelihood that the changes inadvertently break something. Having instructions for running tests is especially helpful if it requires external setup, such as starting a Selenium server for testing in a browser.

## Authors and acknowledgment
Show your appreciation to those who have contributed to the project.

## License
For open source projects, say how it is licensed.

## Project status
If you have run out of energy or time for your project, put a note at the top of the README saying that development has slowed down or stopped completely. Someone may choose to fork your project or volunteer to step in as a maintainer or owner, allowing your project to keep going. You can also make an explicit request for maintainers.
>>>>>>> 93d24ccff32572cb8c0a9b7e3c3ab24c8a1265ea
# fmp_query_ai
