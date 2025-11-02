import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatTimestamp(timestamp: Date): string {
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  }).format(timestamp)
}

export function getConfidenceLevel(score: number): string {
  if (score >= 0.8) return "High"
  if (score >= 0.5) return "Medium"
  return "Low"
}

export function getConfidenceColor(confidence: string): string {
  switch (confidence) {
    case "High": return "text-red-600"
    case "Medium": return "text-yellow-600"
    case "Low": return "text-green-600"
    default: return "text-gray-600"
  }
}
