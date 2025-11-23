#!/usr/bin/env python3
"""
Vercel Entry Point for Virtual Shield - Minimal MVP
Simple landing page that works on Vercel
"""

from flask import Flask, jsonify, render_template_string

# Create a minimal Flask app
app = Flask(__name__)

# Simple HTML template for the main page
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Virtual Shield - AI Content Detector</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        
        .container {
            background: white;
            border-radius: 20px;
            padding: 50px;
            max-width: 600px;
            width: 100%;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            text-align: center;
        }
        
        h1 {
            font-size: 2.5rem;
            color: #333;
            margin-bottom: 20px;
            font-weight: 700;
        }
        
        .subtitle {
            font-size: 1.2rem;
            color: #666;
            margin-bottom: 30px;
        }
        
        .status {
            background: #10b981;
            color: white;
            padding: 15px 30px;
            border-radius: 50px;
            display: inline-block;
            margin: 20px 0;
            font-weight: 600;
        }
        
        .features {
            text-align: left;
            margin: 30px 0;
        }
        
        .feature {
            background: #f8fafc;
            padding: 15px;
            margin: 10px 0;
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }
        
        .feature-title {
            font-weight: 600;
            color: #333;
            margin-bottom: 5px;
        }
        
        .feature-desc {
            color: #666;
            font-size: 0.9rem;
        }
        
        .api-info {
            margin-top: 30px;
            padding: 20px;
            background: #f1f5f9;
            border-radius: 10px;
            text-align: left;
        }
        
        .api-info h3 {
            color: #333;
            margin-bottom: 10px;
        }
        
        .endpoint {
            font-family: 'Courier New', monospace;
            background: #334155;
            color: #10b981;
            padding: 10px;
            border-radius: 5px;
            margin: 5px 0;
            font-size: 0.9rem;
        }
        
        .footer {
            margin-top: 30px;
            color: #999;
            font-size: 0.9rem;
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 30px 20px;
            }
            
            h1 {
                font-size: 2rem;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🛡️ Virtual Shield</h1>
        <p class="subtitle">AI Content Detection System</p>
        
        <div class="status">
            ✅ System Online
        </div>
        
        <div class="features">
            <div class="feature">
                <div class="feature-title">🖼️ Image Analysis</div>
                <div class="feature-desc">Detect AI-generated images with advanced algorithms</div>
            </div>
            
            <div class="feature">
                <div class="feature-title">📝 Text Detection</div>
                <div class="feature-desc">Identify AI-written content in documents</div>
            </div>
            
            <div class="feature">
                <div class="feature-title">⚡ Fast Processing</div>
                <div class="feature-desc">Real-time analysis powered by cloud infrastructure</div>
            </div>
        </div>
        
        <div class="api-info">
            <h3>API Endpoints</h3>
            <div class="endpoint">GET /health</div>
            <div class="endpoint">GET /api/info</div>
            <div class="endpoint">POST /api/analyze</div>
        </div>
        
        <div class="footer">
            Deployed on Vercel | Version 1.0.0
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    """Main landing page"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'message': 'Virtual Shield API is running',
        'version': '1.0.0',
        'timestamp': '2024-01-01T00:00:00Z'
    })

@app.route('/api/info')
def api_info():
    """API information endpoint"""
    return jsonify({
        'name': 'Virtual Shield API',
        'version': '1.0.0',
        'description': 'AI Content Detection System',
        'endpoints': {
            '/': 'Main landing page',
            '/health': 'Health check',
            '/api/info': 'API information'
        },
        'status': 'operational'
    })

# Export app for Vercel
# Vercel will detect this and use it as the serverless function
