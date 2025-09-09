'use client'

import { useState, useEffect } from 'react'
import { Plus, RefreshCw, Rss, Trash2 } from 'lucide-react'

interface RSSFeed {
  id: number
  title: string
  url: string
  category: string
  added_at: string
  last_checked: string | null
  is_active: boolean
}

interface Article {
  id: number
  title: string
  url: string
  summary: string | null
  published_at: string | null
  author: string | null
}

export default function RSSPage() {
  const [feeds, setFeeds] = useState<RSSFeed[]>([])
  const [articles, setArticles] = useState<Article[]>([])
  const [newFeed, setNewFeed] = useState({ url: '', title: '', category: 'general' })
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetchFeeds()
    fetchArticles()
  }, [])

  const fetchFeeds = async () => {
    try {
      const response = await fetch('/api/rss/feeds', {
        headers: { 'X-API-Key': 'devkey' }
      })
      if (response.ok) {
        const data = await response.json()
        setFeeds(data)
      }
    } catch (error) {
      console.error('Error fetching feeds:', error)
    }
  }

  const fetchArticles = async () => {
    try {
      const response = await fetch('/api/rss/articles', {
        headers: { 'X-API-Key': 'devkey' }
      })
      if (response.ok) {
        const data = await response.json()
        setArticles(data)
      }
    } catch (error) {
      console.error('Error fetching articles:', error)
    }
  }

  const addFeed = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    
    try {
      const response = await fetch('/api/rss/feeds', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': 'devkey'
        },
        body: JSON.stringify(newFeed)
      })
      
      if (response.ok) {
        setNewFeed({ url: '', title: '', category: 'general' })
        fetchFeeds()
      }
    } catch (error) {
      console.error('Error adding feed:', error)
    } finally {
      setLoading(false)
    }
  }

  const refreshFeed = async (feedId: number) => {
    try {
      await fetch(`/api/rss/feeds/${feedId}/refresh`, {
        method: 'POST',
        headers: { 'X-API-Key': 'devkey' }
      })
      fetchArticles()
    } catch (error) {
      console.error('Error refreshing feed:', error)
    }
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">RSS Feeds</h1>
        <p className="text-gray-600">Manage your RSS subscriptions and view latest articles</p>
      </div>

      {/* Add New Feed Form */}
      <div className="card mb-8">
        <h2 className="text-xl font-semibold mb-4">Add New RSS Feed</h2>
        <form onSubmit={addFeed} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <input
              type="url"
              placeholder="RSS Feed URL"
              value={newFeed.url}
              onChange={(e) => setNewFeed({ ...newFeed, url: e.target.value })}
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              required
            />
            <input
              type="text"
              placeholder="Feed Title"
              value={newFeed.title}
              onChange={(e) => setNewFeed({ ...newFeed, title: e.target.value })}
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              required
            />
            <select
              value={newFeed.category}
              onChange={(e) => setNewFeed({ ...newFeed, category: e.target.value })}
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="general">General</option>
              <option value="blog">Blog</option>
              <option value="news">News</option>
              <option value="research">Research</option>
              <option value="tech">Technology</option>
            </select>
          </div>
          <button
            type="submit"
            disabled={loading}
            className="btn btn-primary flex items-center gap-2"
          >
            <Plus className="w-4 h-4" />
            {loading ? 'Adding...' : 'Add Feed'}
          </button>
        </form>
      </div>

      {/* RSS Feeds List */}
      <div className="card mb-8">
        <h2 className="text-xl font-semibold mb-4">Your RSS Feeds</h2>
        <div className="space-y-4">
          {feeds.map((feed) => (
            <div key={feed.id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
              <div className="flex items-center gap-3">
                <Rss className="w-5 h-5 text-primary-600" />
                <div>
                  <h3 className="font-medium">{feed.title}</h3>
                  <p className="text-sm text-gray-600">{feed.url}</p>
                  <span className="inline-block px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded-full mt-1">
                    {feed.category}
                  </span>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => refreshFeed(feed.id)}
                  className="btn btn-secondary flex items-center gap-2"
                >
                  <RefreshCw className="w-4 h-4" />
                  Refresh
                </button>
                <button className="btn btn-secondary text-red-600 hover:bg-red-50">
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Latest Articles */}
      <div className="card">
        <h2 className="text-xl font-semibold mb-4">Latest Articles</h2>
        <div className="space-y-4">
          {articles.map((article) => (
            <div key={article.id} className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50">
              <h3 className="font-medium mb-2">
                <a href={article.url} target="_blank" rel="noopener noreferrer" className="text-primary-600 hover:underline">
                  {article.title}
                </a>
              </h3>
              {article.summary && (
                <p className="text-gray-600 text-sm mb-2">{article.summary}</p>
              )}
              <div className="flex items-center gap-4 text-xs text-gray-500">
                {article.author && <span>By {article.author}</span>}
                {article.published_at && (
                  <span>{new Date(article.published_at).toLocaleDateString()}</span>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
} 