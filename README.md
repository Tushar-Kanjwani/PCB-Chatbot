# PCB Chatbot

A Flask-based chatbot that answers questions about cricket players using AI.

## Deployment to Vercel

### Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **GitHub Account**: Your code should be in a GitHub repository
3. **Cloud Database**: You'll need a cloud MySQL database (PlanetScale, Railway, AWS RDS, etc.)

### Setup Steps

1. **Push your code to GitHub**:
   ```bash
   git add .
   git commit -m "Prepare for Vercel deployment"
   git push origin main
   ```

2. **Connect to Vercel**:
   - Go to [vercel.com](https://vercel.com)
   - Click "New Project"
   - Import your GitHub repository
   - Vercel will automatically detect it's a Python project

3. **Configure Environment Variables**:
   In your Vercel project settings, add these environment variables:
   - `FLASK_SECRET_KEY`: A random secret key for Flask sessions
   - `TOGETHER_API_KEY`: Your Together AI API key
   - `DB_HOST`: Your cloud database host
   - `DB_USER`: Database username
   - `DB_PASSWORD`: Database password
   - `DB_NAME`: Database name

4. **Deploy**:
   - Vercel will automatically deploy your app
   - You'll get a URL like `https://your-app.vercel.app`

### Important Notes

- **Database**: Your app currently uses a local MySQL database. For Vercel deployment, you need a cloud database service.
- **File Storage**: The `PCB.csv` file is included in the deployment and will be accessible.
- **API Limits**: Be aware of Vercel's serverless function limits (10-second timeout, 50MB payload).

### Local Development

```bash
pip install -r requirements.txt
python app.py
```

Visit `http://localhost:5000` to test locally.

### Troubleshooting

- If you get database connection errors, make sure your cloud database is accessible from Vercel's servers
- Check Vercel function logs for any deployment issues
- Ensure all environment variables are properly set in Vercel dashboard 