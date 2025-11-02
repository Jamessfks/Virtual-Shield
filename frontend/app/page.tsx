'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Loader2, AlertCircle, CheckCircle, Download, Trash2, FileText } from 'lucide-react'

interface AnalysisResult {
  id: string
  timestamp: Date
  text_preview: string
  status: string
  score: number
  confidence: string
  text_length: number
}

export default function Home() {
  const [text, setText] = useState('')
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [results, setResults] = useState<AnalysisResult[]>([])
  const [error, setError] = useState<string | null>(null)

  const handleAnalyze = async () => {
    if (!text.trim()) {
      setError('Please enter some text to analyze')
      return
    }

    if (text.length < 10) {
      setError('Text must be at least 10 characters')
      return
    }

    setIsAnalyzing(true)
    setError(null)

    try {
      const response = await fetch('/api/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || 'Analysis failed')
      }

      const data = await response.json()
      
      const result: AnalysisResult = {
        id: Date.now().toString(),
        timestamp: new Date(data.timestamp),
        text_preview: text.substring(0, 100) + (text.length > 100 ? '...' : ''),
        status: data.status,
        score: data.score,
        confidence: data.confidence,
        text_length: data.text_length,
      }

      setResults([result, ...results])
      setText('')  // Clear input after analysis

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
    link.download = `ai-text-detection-results-${Date.now()}.json`
    link.click()
    URL.revokeObjectURL(url)
  }

  const formatTimestamp = (date: Date) => {
    return new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(date)
  }

  return (
    <main className="min-h-screen bg-white">
      <div className="container mx-auto px-4 py-12 max-w-7xl">
        {/* Header */}
        <div className="text-center mb-16">
          <h1 className="text-7xl font-black text-black mb-4 tracking-tight">
            AI TEXT DETECTOR
          </h1>
          <p className="text-lg font-semibold text-gray-500 uppercase tracking-wide">
            Detect AI-Generated Content
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Input Section */}
          <Card className="border-2 border-black shadow-none">
            <CardHeader>
              <CardTitle className="flex items-center gap-3 text-2xl font-black uppercase">
                <FileText className="w-7 h-7" />
                Input Text
              </CardTitle>
              <CardDescription className="text-gray-600 font-semibold text-sm uppercase tracking-wide">
                Enter text to analyze
              </CardDescription>
            </CardHeader>
            <CardContent>
              <textarea
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder="Paste or type your text here..."
                className="w-full h-64 p-4 border-2 border-gray-400 focus:border-black rounded-sm font-mono text-sm resize-none focus:outline-none transition-colors"
                maxLength={50000}
              />
              
              <div className="mt-2 text-xs text-gray-500 font-semibold">
                {text.length} / 50,000 characters
              </div>

              <div className="mt-6">
                <Button
                  className="w-full bg-black text-white font-bold uppercase tracking-wide hover:bg-gray-800 border-2 border-black"
                  onClick={handleAnalyze}
                  disabled={!text.trim() || isAnalyzing}
                >
                  {isAnalyzing ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Analyzing
                    </>
                  ) : (
                    <>
                      <CheckCircle className="w-4 h-4 mr-2" />
                      Analyze Text
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
                  <div className="bg-gray-50 p-4 border-2 border-black min-h-[120px] relative">
                    <p className="text-sm font-mono text-gray-700">{results[0].text_preview}</p>
                    <div className={`absolute top-3 right-3 px-4 py-2 font-black text-xs uppercase tracking-wider border-2 ${
                      results[0].status === 'AI_GENERATED' 
                        ? "bg-black text-white border-black" 
                        : "bg-white text-black border-black"
                    }`}>
                      {results[0].status === 'AI_GENERATED' ? 'AI GENERATED' : 'AUTHENTIC'}
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-white p-5 border-2 border-black">
                      <p className="text-xs text-gray-500 mb-2 font-bold uppercase tracking-wider">Score</p>
                      <p className="text-3xl font-black">{results[0].score.toFixed(3)}</p>
                    </div>
                    <div className="bg-white p-5 border-2 border-black">
                      <p className="text-xs text-gray-500 mb-2 font-bold uppercase tracking-wider">Confidence</p>
                      <p className="text-3xl font-black">{results[0].confidence}</p>
                    </div>
                  </div>

                  <div className="space-y-3 text-sm">
                    <div className="flex justify-between border-t-2 border-black pt-3">
                      <span className="text-gray-500 font-bold uppercase text-xs">Length</span>
                      <span className="font-bold text-black">{results[0].text_length} characters</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500 font-bold uppercase text-xs">Time</span>
                      <span className="font-bold text-black">{formatTimestamp(results[0].timestamp)}</span>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center py-16">
                  <FileText className="w-20 h-20 mx-auto text-gray-300 mb-6" />
                  <p className="text-black font-black text-xl uppercase tracking-wide">No Results</p>
                  <p className="text-sm text-gray-500 mt-3 font-semibold uppercase tracking-wide">Enter text to analyze</p>
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
                      <th className="text-left py-4 px-4 font-black text-xs text-black uppercase tracking-wider">Text Preview</th>
                      <th className="text-center py-4 px-4 font-black text-xs text-black uppercase tracking-wider">Status</th>
                      <th className="text-center py-4 px-4 font-black text-xs text-black uppercase tracking-wider">Score</th>
                      <th className="text-center py-4 px-4 font-black text-xs text-black uppercase tracking-wider">Confidence</th>
                    </tr>
                  </thead>
                  <tbody>
                    {results.map((result) => (
                      <tr key={result.id} className="border-b border-gray-300 hover:bg-gray-50 transition-colors">
                        <td className="py-4 px-4 text-xs font-semibold">{formatTimestamp(result.timestamp)}</td>
                        <td className="py-4 px-4 text-xs font-mono max-w-md truncate">{result.text_preview}</td>
                        <td className="py-4 px-4 text-center">
                          <span className={`inline-flex items-center px-3 py-1 text-xs font-black uppercase tracking-wide border-2 ${
                            result.status === 'AI_GENERATED'
                              ? "bg-black text-white border-black"
                              : "bg-white text-black border-black"
                          }`}>
                            {result.status === 'AI_GENERATED' ? 'AI' : 'Real'}
                          </span>
                        </td>
                        <td className="py-4 px-4 text-center font-mono text-sm font-bold">{result.score.toFixed(3)}</td>
                        <td className="py-4 px-4 text-center">
                          <span className="font-black text-sm uppercase">{result.confidence}</span>
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
