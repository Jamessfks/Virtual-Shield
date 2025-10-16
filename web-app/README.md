# AI Screenshot Detector - Web Application

A modern, clean web application for detecting AI-generated content in images using Reality Defender API.

## Features

- 🎨 **Beautiful Modern UI** - Built with React, Next.js, and TailwindCSS
- 📤 **Drag & Drop Upload** - Easy image upload with drag and drop support
- 🔍 **Real-time Analysis** - Instant AI detection results
- 📊 **Results History** - Track all analyzed images with detailed metrics
- 💾 **Export Results** - Download analysis history as JSON
- 🎯 **Confidence Scoring** - Visual indicators for detection confidence levels

## Tech Stack

- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: TailwindCSS
- **Icons**: Lucide React
- **API Integration**: Reality Defender

## Getting Started

### Prerequisites

- Node.js 18+ installed
- npm or yarn package manager

### Installation

1. Navigate to the web-app directory:
```bash
cd web-app
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

4. Open your browser and visit:
```
http://localhost:3000
```

## Usage

1. **Upload an Image**: Click "Choose File" or drag and drop an image onto the upload area
2. **Analyze**: Click "Analyze Image" to send the image to Reality Defender
3. **View Results**: See real-time detection results with AI score and confidence level
4. **Track History**: All analyzed images are saved in the history table
5. **Export Data**: Download your analysis results as JSON for record-keeping

## Detection Results

- **🚨 AI DETECTED** - Image appears to be AI-generated (MANIPULATED status)
- **✅ AUTHENTIC** - Image appears to be authentic (AUTHENTIC status)
- **AI Score** - Numerical score from 0 to 1 indicating likelihood of AI generation
- **Confidence** - High/Medium/Low confidence level based on the score

## API Integration

This application uses the Reality Defender API for AI detection. The API key is configured in the backend route at `/app/api/analyze/route.ts`.

## Building for Production

To create a production build:

```bash
npm run build
npm start
```

## Project Structure

```
web-app/
├── app/
│   ├── api/
│   │   └── analyze/
│   │       └── route.ts       # Backend API route
│   ├── globals.css            # Global styles
│   ├── layout.tsx             # Root layout
│   └── page.tsx               # Main page component
├── components/
│   └── ui/
│       ├── button.tsx         # Button component
│       └── card.tsx           # Card component
├── lib/
│   └── utils.ts               # Utility functions
├── public/                    # Static assets
├── package.json               # Dependencies
└── tailwind.config.ts         # Tailwind configuration
```

## License

This project is built for educational and demonstration purposes.
