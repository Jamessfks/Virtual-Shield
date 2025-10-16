'use client'

import { useState, useRef } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Upload, Image as ImageIcon, Loader2, AlertCircle, CheckCircle, Download, Trash2 } from 'lucide-react'
import { cn, formatTimestamp, getConfidenceLevel, getConfidenceColor } from '@/lib/utils'

interface AnalysisResult {
  id: string
  timestamp: Date
  filename: string
  status: string
  score: number
  confidence: string
  imageUrl: string
  size: number
  type: string
}

export default function Home() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [results, setResults] = useState<AnalysisResult[]>([])
  const [error, setError] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      if (!file.type.startsWith('image/')) {
        setError('Please select an image file')
        return
      }
      setSelectedFile(file)
      setError(null)
      
      // Create preview URL
      const url = URL.createObjectURL(file)
      setPreviewUrl(url)
    }
  }

  const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault()
    const file = event.dataTransfer.files?.[0]
    if (file) {
      if (!file.type.startsWith('image/')) {
        setError('Please select an image file')
        return
      }
      setSelectedFile(file)
      setError(null)
      
      const url = URL.createObjectURL(file)
      setPreviewUrl(url)
    }
  }

  const handleDragOver = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault()
  }

  const handleAnalyze = async () => {
    if (!selectedFile) return

    setIsAnalyzing(true)
    setError(null)

    try {
      const formData = new FormData()
      formData.append('file', selectedFile)

      const response = await fetch('/api/analyze', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || 'Analysis failed')
      }

      const data = await response.json()
      
      const result: AnalysisResult = {
        id: Date.now().toString(),
        timestamp: new Date(data.timestamp),
        filename: data.filename,
        status: data.status,
        score: data.score,
        confidence: getConfidenceLevel(data.score),
        imageUrl: previewUrl || '',
        size: data.size,
        type: data.type,
      }

      setResults([result, ...results])
      
      // Reset form
      setSelectedFile(null)
      setPreviewUrl(null)
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }

    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred during analysis')
      console.error('Analysis error:', err)
    } finally {
      setIsAnalyzing(false)
    }
  }

  const clearResults = () => {
    if (confirm('Are you sure you want to clear all results?')) {
      setResults([])
    }
  }

  const exportResults = () => {
    const dataStr = JSON.stringify(results, null, 2)
    const dataBlob = new Blob([dataStr], { type: 'application/json' })
    const url = URL.createObjectURL(dataBlob)
    const link = document.createElement('a')
    link.href = url
    link.download = `ai-detection-results-${Date.now()}.json`
    link.click()
    URL.revokeObjectURL(url)
  }

  return (
    <main className="min-h-screen bg-white">
      <div className="container mx-auto px-4 py-12 max-w-7xl">
        {/* Header */}
        <div className="text-center mb-16">
          <h1 className="text-7xl font-black text-black mb-4 tracking-tight">
            AI DETECTOR
          </h1>
          <p className="text-lg font-semibold text-gray-500 uppercase tracking-wide">
            Reality Defender Analysis
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Upload Section */}
          <Card className="border-2 border-black shadow-none">
            <CardHeader>
              <CardTitle className="flex items-center gap-3 text-2xl font-black uppercase">
                <Upload className="w-7 h-7" />
                Upload
              </CardTitle>
              <CardDescription className="text-gray-600 font-semibold text-sm uppercase tracking-wide">
                Drop image to analyze
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div
                onDrop={handleDrop}
                onDragOver={handleDragOver}
                className={cn(
                  "border-2 border-dashed rounded-sm p-8 text-center transition-colors",
                  selectedFile ? "border-black bg-gray-50" : "border-gray-400 hover:border-black"
                )}
              >
                {previewUrl ? (
                  <div className="space-y-4">
                    <img
                      src={previewUrl}
                      alt="Preview"
                      className="max-h-64 mx-auto rounded-lg shadow-md"
                    />
                    <p className="text-sm text-gray-600">{selectedFile?.name}</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    <ImageIcon className="w-16 h-16 mx-auto text-black" />
                    <div>
                      <p className="text-xl font-bold text-black uppercase tracking-wide">
                        Drop Image
                      </p>
                      <p className="text-sm text-gray-500 mt-2 font-semibold">
                        JPG · PNG · GIF · WEBP
                      </p>
                    </div>
                  </div>
                )}
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  onChange={handleFileSelect}
                  className="hidden"
                  id="file-upload"
                />
              </div>

              <div className="mt-6 space-y-3">
                <label htmlFor="file-upload">
                  <Button
                    variant="outline"
                    className="w-full border-2 border-black font-bold uppercase tracking-wide hover:bg-black hover:text-white"
                    onClick={() => fileInputRef.current?.click()}
                    type="button"
                  >
                    <Upload className="w-4 h-4 mr-2" />
                    Browse
                  </Button>
                </label>

                <Button
                  className="w-full bg-black text-white font-bold uppercase tracking-wide hover:bg-gray-800 border-2 border-black"
                  onClick={handleAnalyze}
                  disabled={!selectedFile || isAnalyzing}
                >
                  {isAnalyzing ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Analyzing
                    </>
                  ) : (
                    <>
                      <CheckCircle className="w-4 h-4 mr-2" />
                      Analyze
                    </>
                  )}
                </Button>
              </div>

              {error && (
                <div className="mt-4 p-4 bg-black text-white border-2 border-black rounded-sm flex items-start gap-2">
                  <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
                  <p className="text-sm font-semibold">{error}</p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Latest Result */}
          <Card className="border-2 border-black shadow-none">
            <CardHeader>
              <CardTitle className="flex items-center gap-3 text-2xl font-black uppercase">
                <AlertCircle className="w-7 h-7" />
                Results
              </CardTitle>
              <CardDescription className="text-gray-600 font-semibold text-sm uppercase tracking-wide">
                Latest analysis
              </CardDescription>
            </CardHeader>
            <CardContent>
              {results.length > 0 ? (
                <div className="space-y-6">
                  <div className="relative">
                    <img
                      src={results[0].imageUrl}
                      alt={results[0].filename}
                      className="w-full h-48 object-cover border-2 border-black"
                    />
                    <div className={cn(
                      "absolute top-3 right-3 px-4 py-2 font-black text-xs uppercase tracking-wider border-2",
                      results[0].status === 'MANIPULATED' 
                        ? "bg-black text-white border-black" 
                        : "bg-white text-black border-black"
                    )}>
                      {results[0].status === 'MANIPULATED' ? 'AI DETECTED' : 'AUTHENTIC'}
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-white p-5 border-2 border-black">
                      <p className="text-xs text-gray-500 mb-2 font-bold uppercase tracking-wider">Score</p>
                      <p className="text-3xl font-black">{results[0].score.toFixed(3)}</p>
                    </div>
                    <div className="bg-white p-5 border-2 border-black">
                      <p className="text-xs text-gray-500 mb-2 font-bold uppercase tracking-wider">Confidence</p>
                      <p className="text-3xl font-black">
                        {results[0].confidence}
                      </p>
                    </div>
                  </div>

                  <div className="space-y-3 text-sm">
                    <div className="flex justify-between border-t-2 border-black pt-3">
                      <span className="text-gray-500 font-bold uppercase text-xs">File</span>
                      <span className="font-bold text-black">{results[0].filename}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500 font-bold uppercase text-xs">Time</span>
                      <span className="font-bold text-black">{formatTimestamp(results[0].timestamp)}</span>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center py-16">
                  <ImageIcon className="w-20 h-20 mx-auto text-gray-300 mb-6" />
                  <p className="text-black font-black text-xl uppercase tracking-wide">No Results</p>
                  <p className="text-sm text-gray-500 mt-3 font-semibold uppercase tracking-wide">Upload to analyze</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Results History */}
        {results.length > 0 && (
          <Card className="border-2 border-black shadow-none">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-2xl font-black uppercase">History</CardTitle>
                  <CardDescription className="text-gray-600 font-semibold text-sm uppercase tracking-wide">
                    {results.length} {results.length === 1 ? 'result' : 'results'}
                  </CardDescription>
                </div>
                <div className="flex gap-3">
                  <Button variant="outline" size="sm" onClick={exportResults} className="border-2 border-black font-bold uppercase hover:bg-black hover:text-white">
                    <Download className="w-4 h-4 mr-2" />
                    Export
                  </Button>
                  <Button size="sm" onClick={clearResults} className="bg-black text-white font-bold uppercase hover:bg-gray-800 border-2 border-black">
                    <Trash2 className="w-4 h-4 mr-2" />
                    Clear
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b-2 border-black">
                      <th className="text-left py-4 px-4 font-black text-xs text-black uppercase tracking-wider">Time</th>
                      <th className="text-left py-4 px-4 font-black text-xs text-black uppercase tracking-wider">File</th>
                      <th className="text-center py-4 px-4 font-black text-xs text-black uppercase tracking-wider">Status</th>
                      <th className="text-center py-4 px-4 font-black text-xs text-black uppercase tracking-wider">Score</th>
                      <th className="text-center py-4 px-4 font-black text-xs text-black uppercase tracking-wider">Confidence</th>
                    </tr>
                  </thead>
                  <tbody>
                    {results.map((result) => (
                      <tr key={result.id} className="border-b border-gray-300 hover:bg-gray-50 transition-colors">
                        <td className="py-4 px-4 text-xs font-semibold">{formatTimestamp(result.timestamp)}</td>
                        <td className="py-4 px-4 text-xs font-bold">{result.filename}</td>
                        <td className="py-4 px-4 text-center">
                          <span className={cn(
                            "inline-flex items-center px-3 py-1 text-xs font-black uppercase tracking-wide border-2",
                            result.status === 'MANIPULATED'
                              ? "bg-black text-white border-black"
                              : "bg-white text-black border-black"
                          )}>
                            {result.status === 'MANIPULATED' ? 'AI' : 'Real'}
                          </span>
                        </td>
                        <td className="py-4 px-4 text-center font-mono text-sm font-bold">{result.score.toFixed(3)}</td>
                        <td className="py-4 px-4 text-center">
                          <span className="font-black text-sm uppercase">
                            {result.confidence}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </main>
  )
}
