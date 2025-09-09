'use client'

import { useState, useEffect } from 'react'
import { Search, Filter, BookOpen, Rss, Brain } from 'lucide-react'

interface SearchResult {
  highlight: {
    id: number
    text: string
    note: string | null
    location: string | null
    color: string | null
    created_at: string
  }
  source: {
    id: number
    type: string
    url: string
    title: string
    author: string | null
    summary: string | null
  }
  score: number
  match_type: string
}

export default function SearchPage() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<SearchResult[]>([])
  const [loading, setLoading] = useState(false)
  const [searchType, setSearchType] = useState<'all' | 'highlights' | 'articles'>('all')
  const [filters, setFilters] = useState({
    tags: [] as string[],
    sourceType: '' as string,
    dateRange: '' as string
  })

  const performSearch = async () => {
    if (!query.trim()) return
    
    setLoading(true)
    try {
      const response = await fetch('/api/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': 'devkey'
        },
        body: JSON.stringify({
          q: query,
          tags: filters.tags.length > 0 ? filters.tags : undefined,
          limit: 50
        })
      })
      
      if (response.ok) {
        const data = await response.json()
        setResults(data)
      }
    } catch (error) {
      console.error('Search error:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (query.trim()) {
      const debounceTimer = setTimeout(performSearch, 500)
      return () => clearTimeout(debounceTimer)
    }
  }, [query, filters])

  const getMatchTypeIcon = (matchType: string) => {
    switch (matchType) {
      case 'hybrid':
        return <Brain className="w-4 h-4 text-blue-600" />
      case 'text':
        return <Search className="w-4 h-4 text-green-600" />
      case 'vector':
        return <Brain className="w-4 h-4 text-purple-600" />
      default:
        return <BookOpen className="w-4 h-4 text-gray-600" />
    }
  }

  const getMatchTypeLabel = (matchType: string) => {
    switch (matchType) {
      case 'hybrid':
        return 'Hybrid Match'
      case 'text':
        return 'Text Match'
      case 'vector':
        return 'AI Match'
      default:
        return 'Recent'
    }
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Search Knowledge</h1>
        <p className="text-gray-600">Find highlights and articles using hybrid search (text + AI)</p>
      </div>

      {/* Search Bar */}
      <div className="mb-8">
        <div className="relative max-w-2xl">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
          <input
            type="text"
            placeholder="Search your highlights, articles, and sources..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
        </div>
      </div>

      {/* Filters */}
      <div className="mb-6">
        <div className="flex items-center gap-4 mb-4">
          <Filter className="w-5 h-5 text-gray-600" />
          <span className="font-medium text-gray-700">Filters:</span>
        </div>
        
        <div className="flex flex-wrap gap-4">
          <select
            value={searchType}
            onChange={(e) => setSearchType(e.target.value as any)}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="all">All Content</option>
            <option value="highlights">Highlights Only</option>
            <option value="articles">Articles Only</option>
          </select>
          
          <select
            value={filters.sourceType}
            onChange={(e) => setFilters({ ...filters, sourceType: e.target.value })}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="">All Sources</option>
            <option value="web">Web</option>
            <option value="pdf">PDF</option>
            <option value="youtube">YouTube</option>
            <option value="rss">RSS</option>
          </select>
          
          <select
            value={filters.dateRange}
            onChange={(e) => setFilters({ ...filters, dateRange: e.target.value })}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="">All Time</option>
            <option value="today">Today</option>
            <option value="week">This Week</option>
            <option value="month">This Month</option>
            <option value="year">This Year</option>
          </select>
        </div>
      </div>

      {/* Search Results */}
      <div className="space-y-6">
        {loading && (
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
            <p className="mt-2 text-gray-600">Searching...</p>
          </div>
        )}

        {!loading && results.length === 0 && query && (
          <div className="text-center py-8">
            <Search className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">No results found for "{query}"</p>
            <p className="text-sm text-gray-500 mt-2">Try different keywords or check your filters</p>
          </div>
        )}

        {!loading && results.length > 0 && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <p className="text-sm text-gray-600">
                Found {results.length} results for "{query}"
              </p>
              <div className="flex items-center gap-2 text-sm text-gray-500">
                <span>Sort by:</span>
                <select className="border-none bg-transparent focus:outline-none">
                  <option>Relevance</option>
                  <option>Date</option>
                  <option>Score</option>
                </select>
              </div>
            </div>

            {results.map((result, index) => (
              <div key={result.highlight.id} className="card hover:shadow-lg transition-shadow">
                <div className="flex items-start gap-3">
                  <div className="flex-shrink-0 mt-1">
                    {getMatchTypeIcon(result.match_type)}
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded-full">
                        {getMatchTypeLabel(result.match_type)}
                      </span>
                      <span className="text-xs text-gray-500">
                        Score: {result.score.toFixed(3)}
                      </span>
                    </div>
                    
                    <h3 className="font-medium text-gray-900 mb-2">
                      {result.highlight.text.length > 200 
                        ? `${result.highlight.text.substring(0, 200)}...` 
                        : result.highlight.text
                      }
                    </h3>
                    
                    {result.highlight.note && (
                      <p className="text-gray-600 text-sm mb-2 italic">
                        Note: {result.highlight.note}
                      </p>
                    )}
                    
                    <div className="flex items-center gap-4 text-sm text-gray-500">
                      <div className="flex items-center gap-1">
                        <BookOpen className="w-4 h-4" />
                        <span>{result.source.title}</span>
                      </div>
                      
                      {result.source.author && (
                        <span>by {result.source.author}</span>
                      )}
                      
                      <span>{new Date(result.highlight.created_at).toLocaleDateString()}</span>
                      
                      {result.highlight.location && (
                        <span>at {result.highlight.location}</span>
                      )}
                    </div>
                    
                    <div className="mt-3 flex items-center gap-2">
                      <a
                        href={result.source.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-primary-600 hover:text-primary-700 text-sm font-medium"
                      >
                        View Source →
                      </a>
                      
                      <button className="text-gray-500 hover:text-gray-700 text-sm">
                        Add to Review
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
} 