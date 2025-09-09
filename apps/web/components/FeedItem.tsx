interface FeedItemProps {
  type: 'paper' | 'web' | 'video' | 'rss';
  title: string;
  excerpt: string;
  source: string;
  timeAgo: string;
  scoreTag: string;
}

export default function FeedItem({ type, title, excerpt, source, timeAgo, scoreTag }: FeedItemProps) {
  const getTypeIcon = () => {
    switch (type) {
      case 'paper':
        return (
          <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        );
      case 'web':
        return (
          <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9v-9m0-9v9" />
          </svg>
        );
      case 'video':
        return (
          <svg className="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
          </svg>
        );
      case 'rss':
        return (
          <svg className="w-5 h-5 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        );
      default:
        return null;
    }
  };

  const getTypeColor = () => {
    switch (type) {
      case 'paper':
        return 'bg-blue-50 border-blue-200';
      case 'web':
        return 'bg-green-50 border-green-200';
      case 'video':
        return 'bg-red-50 border-red-200';
      case 'rss':
        return 'bg-orange-50 border-orange-200';
      default:
        return 'bg-gray-50 border-gray-200';
    }
  };

  return (
    <div className={`p-4 rounded-lg border ${getTypeColor()} hover:shadow-md transition-shadow cursor-pointer`}>
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0 mt-1">
          {getTypeIcon()}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-2">
            <h3 className="text-sm font-medium text-gray-900 line-clamp-2">
              {title}
            </h3>
            <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
              {scoreTag}
            </span>
          </div>
          <p className="text-sm text-gray-600 line-clamp-2 mb-3">
            {excerpt}
          </p>
          <div className="flex items-center justify-between text-xs text-gray-500">
            <span className="font-medium">{source}</span>
            <span>{timeAgo}</span>
          </div>
        </div>
        <div className="flex-shrink-0">
          <button className="p-1 text-gray-400 hover:text-gray-600 transition-colors">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}