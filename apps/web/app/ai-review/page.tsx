'use client'

import { useState, useEffect } from 'react'
import { Brain, Target, TrendingUp, Clock, CheckCircle, XCircle } from 'lucide-react'

interface Highlight {
  id: number
  text: string
  source: {
    title: string
    url: string
  }
}

interface QuizQuestion {
  question: string
  correct_answer: string
  options: string[]
  explanation: string
}

interface LearningStats {
  total_highlights: number
  total_reviews: number
  total_sessions: number
  success_rate: number
  correct_answers: number
}

export default function AIReviewPage() {
  const [highlights, setHighlights] = useState<Highlight[]>([])
  const [currentQuiz, setCurrentQuiz] = useState<QuizQuestion | null>(null)
  const [selectedAnswer, setSelectedAnswer] = useState<string>('')
  const [showResult, setShowResult] = useState(false)
  const [stats, setStats] = useState<LearningStats | null>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetchHighlights()
    fetchLearningStats()
  }, [])

  const fetchHighlights = async () => {
    try {
      const response = await fetch('/api/highlights', {
        headers: { 'X-API-Key': 'devkey' }
      })
      if (response.ok) {
        const data = await response.json()
        setHighlights(data)
      }
    } catch (error) {
      console.error('Error fetching highlights:', error)
    }
  }

  const fetchLearningStats = async () => {
    try {
      const response = await fetch('/api/ai/review/learning-stats', {
        headers: { 'X-API-Key': 'devkey' }
      })
      if (response.ok) {
        const data = await response.json()
        setStats(data)
      }
    } catch (error) {
      console.error('Error fetching stats:', error)
    }
  }

  const generateQuiz = async (highlightId: number) => {
    setLoading(true)
    try {
      const response = await fetch('/api/ai/review/generate-quiz', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': 'devkey'
        },
        body: JSON.stringify({ highlight_id: highlightId })
      })
      
      if (response.ok) {
        const quiz = await response.json()
        setCurrentQuiz(quiz)
        setSelectedAnswer('')
        setShowResult(false)
      }
    } catch (error) {
      console.error('Error generating quiz:', error)
    } finally {
      setLoading(false)
    }
  }

  const submitAnswer = async () => {
    if (!selectedAnswer || !currentQuiz) return
    
    const isCorrect = selectedAnswer === currentQuiz.correct_answer
    setShowResult(true)
    
    // Submit answer to track progress
    try {
      await fetch('/api/ai/review/submit-answer', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': 'devkey'
        },
        body: JSON.stringify({
          highlight_id: highlights.find(h => h.text.includes(currentQuiz.question))?.id || 1,
          user_answer: selectedAnswer,
          time_spent: 30 // This would be tracked in real implementation
        })
      })
      
      // Refresh stats
      fetchLearningStats()
    } catch (error) {
      console.error('Error submitting answer:', error)
    }
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">AI-Powered Review</h1>
        <p className="text-gray-600">Practice with AI-generated quizzes and track your learning progress</p>
      </div>

      {/* Learning Stats */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="card text-center">
            <Target className="w-8 h-8 text-primary-600 mx-auto mb-2" />
            <div className="text-2xl font-bold text-gray-900">{stats.total_highlights}</div>
            <div className="text-sm text-gray-600">Total Highlights</div>
          </div>
          <div className="card text-center">
            <Brain className="w-8 h-8 text-green-600 mx-auto mb-2" />
            <div className="text-2xl font-bold text-gray-900">{stats.total_reviews}</div>
            <div className="text-sm text-gray-600">Total Reviews</div>
          </div>
          <div className="card text-center">
            <Clock className="w-8 h-8 text-blue-600 mx-auto mb-2" />
            <div className="text-2xl font-bold text-gray-900">{stats.total_sessions}</div>
            <div className="text-sm text-gray-600">Study Sessions</div>
          </div>
          <div className="card text-center">
            <TrendingUp className="w-8 h-8 text-purple-600 mx-auto mb-2" />
            <div className="text-2xl font-bold text-gray-900">{stats.success_rate}%</div>
            <div className="text-sm text-gray-600">Success Rate</div>
          </div>
        </div>
      )}

      {/* Quiz Section */}
      {currentQuiz ? (
        <div className="card mb-8">
          <h2 className="text-xl font-semibold mb-4">Quiz Question</h2>
          <div className="space-y-6">
            <div>
              <p className="text-lg text-gray-900 mb-4">{currentQuiz.question}</p>
              <div className="space-y-3">
                {currentQuiz.options.map((option, index) => (
                  <label key={index} className="flex items-center space-x-3 cursor-pointer">
                    <input
                      type="radio"
                      name="answer"
                      value={option}
                      checked={selectedAnswer === option}
                      onChange={(e) => setSelectedAnswer(e.target.value)}
                      className="w-4 h-4 text-primary-600"
                    />
                    <span className="text-gray-700">{option}</span>
                  </label>
                ))}
              </div>
            </div>
            
            {!showResult && (
              <button
                onClick={submitAnswer}
                disabled={!selectedAnswer}
                className="btn btn-primary"
              >
                Submit Answer
              </button>
            )}
            
            {showResult && (
              <div className="p-4 border rounded-lg">
                <div className="flex items-center gap-2 mb-3">
                  {selectedAnswer === currentQuiz.correct_answer ? (
                    <CheckCircle className="w-5 h-5 text-green-600" />
                  ) : (
                    <XCircle className="w-5 h-5 text-red-600" />
                  )}
                  <span className={`font-medium ${
                    selectedAnswer === currentQuiz.correct_answer ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {selectedAnswer === currentQuiz.correct_answer ? 'Correct!' : 'Incorrect'}
                  </span>
                </div>
                <p className="text-gray-700 mb-3">
                  <strong>Correct Answer:</strong> {currentQuiz.correct_answer}
                </p>
                <p className="text-gray-600">{currentQuiz.explanation}</p>
                <button
                  onClick={() => setCurrentQuiz(null)}
                  className="btn btn-secondary mt-4"
                >
                  Next Question
                </button>
              </div>
            )}
          </div>
        </div>
      ) : (
        <div className="card mb-8">
          <h2 className="text-xl font-semibold mb-4">Generate Quiz</h2>
          <p className="text-gray-600 mb-4">
            Select a highlight to generate an AI-powered quiz question
          </p>
          <div className="space-y-3">
            {highlights.map((highlight) => (
              <div key={highlight.id} className="p-4 border border-gray-200 rounded-lg">
                <p className="text-gray-900 mb-2">{highlight.text.substring(0, 100)}...</p>
                <p className="text-sm text-gray-600 mb-3">Source: {highlight.source.title}</p>
                <button
                  onClick={() => generateQuiz(highlight.id)}
                  disabled={loading}
                  className="btn btn-primary"
                >
                  {loading ? 'Generating...' : 'Generate Quiz'}
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
} 