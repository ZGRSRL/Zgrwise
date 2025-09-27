"use client";

import { useState } from "react";
import { 
  Search, 
  Filter, 
  Clock, 
  Globe, 
  Database, 
  BarChart3, 
  CheckCircle2, 
  TrendingUp,
  BookOpen,
  FileText,
  Video,
  Mic,
  Image,
  Code,
  Zap,
  Target,
  Calendar,
  User,
  Settings,
  Bell,
  ChevronDown,
  Star,
  Eye,
  Bookmark,
  Share2,
  MoreHorizontal
} from "lucide-react";

// --- Badge Component ---
function Badge({ 
  children, 
  className = "" 
}: { 
  children: React.ReactNode; 
  className?: string; 
}) {
  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ring-1 ring-inset ${className}`}>
      {children}
    </span>
  );
}

// --- Highlight Card Component ---
function HighlightCard({ 
  title, 
  excerpt, 
  kind, 
  author, 
  ago, 
  aiScore, 
  textScore, 
  tone = "blue" 
}: {
  title: string;
  excerpt: string;
  kind: string;
  author: string;
  ago: string;
  aiScore?: number;
  textScore?: number;
  tone?: "blue" | "green" | "purple" | "orange";
}) {
  const toneClasses = {
    blue: "border-blue-200 bg-blue-50/50 dark:border-blue-800 dark:bg-blue-950/20",
    green: "border-green-200 bg-green-50/50 dark:border-green-800 dark:bg-green-950/20",
    purple: "border-purple-200 bg-purple-50/50 dark:border-purple-800 dark:bg-purple-950/20",
    orange: "border-orange-200 bg-orange-50/50 dark:border-orange-800 dark:bg-orange-950/20"
  };

  const getKindIcon = (kind: string) => {
    switch (kind.toLowerCase()) {
      case "research paper": return <FileText className="h-4 w-4" />;
      case "blog post": return <BookOpen className="h-4 w-4" />;
      case "video": return <Video className="h-4 w-4" />;
      case "podcast": return <Mic className="h-4 w-4" />;
      case "image": return <Image className="h-4 w-4" />;
      case "code": return <Code className="h-4 w-4" />;
      default: return <FileText className="h-4 w-4" />;
    }
  };

  return (
    <div className={`group relative rounded-2xl border p-6 transition-all duration-200 hover:shadow-lg ${toneClasses[tone]}`}>
      {/* Score Badge */}
      <div className="absolute right-4 top-4">
        {aiScore && (
          <Badge className="bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300">
            <Zap className="h-3 w-3 mr-1" />
            AI {Math.round(aiScore * 100)}%
          </Badge>
        )}
        {textScore && (
          <Badge className="bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300 ml-2">
            <Target className="h-3 w-3 mr-1" />
            Text {Math.round(textScore * 100)}%
          </Badge>
        )}
      </div>

      {/* Content */}
      <div className="pr-20">
        <div className="flex items-center gap-2 mb-3">
          {getKindIcon(kind)}
          <span className="text-sm font-medium text-zinc-600 dark:text-zinc-400">{kind}</span>
          <span className="text-zinc-300 dark:text-zinc-600">•</span>
          <span className="text-sm text-zinc-500 dark:text-zinc-500">{ago}</span>
        </div>

        <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100 mb-2 line-clamp-2">
          {title}
        </h3>

        <p className="text-zinc-600 dark:text-zinc-300 text-sm leading-relaxed line-clamp-3">
          {excerpt}
        </p>

        <div className="flex items-center justify-between mt-4">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded-full bg-zinc-200 dark:bg-zinc-700 flex items-center justify-center">
              <User className="h-3 w-3 text-zinc-600 dark:text-zinc-400" />
            </div>
            <span className="text-sm text-zinc-600 dark:text-zinc-400">{author}</span>
          </div>

          <div className="flex items-center gap-1">
            <button className="p-1.5 rounded-lg hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors">
              <Bookmark className="h-4 w-4 text-zinc-500" />
            </button>
            <button className="p-1.5 rounded-lg hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors">
              <Share2 className="h-4 w-4 text-zinc-500" />
            </button>
            <button className="p-1.5 rounded-lg hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors">
              <MoreHorizontal className="h-4 w-4 text-zinc-500" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

// --- Top Bar Component ---
function TopBar() {
  const [searchQuery, setSearchQuery] = useState("");
  const [activeFilter, setActiveFilter] = useState("all");

  const filters = [
    { id: "all", label: "All Content", count: 24 },
    { id: "sources", label: "Sources", count: 8 },
    { id: "time", label: "Time", count: 16 }
  ];

  return (
    <div className="space-y-4">
      {/* Search Bar */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-zinc-400" />
        <input
          type="text"
          placeholder="Search highlights, sources, or topics..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full pl-10 pr-4 py-3 bg-white dark:bg-zinc-800 border border-zinc-200 dark:border-zinc-700 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
        />
      </div>

      {/* Filter Pills */}
      <div className="flex gap-2">
        {filters.map((filter) => (
          <button
            key={filter.id}
            onClick={() => setActiveFilter(filter.id)}
            className={`px-4 py-2 rounded-full text-sm font-medium transition-all duration-200 ${
              activeFilter === filter.id
                ? "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300"
                : "bg-zinc-100 text-zinc-600 hover:bg-zinc-200 dark:bg-zinc-800 dark:text-zinc-400 dark:hover:bg-zinc-700"
            }`}
          >
            {filter.label}
            <span className="ml-2 px-2 py-0.5 bg-zinc-200 dark:bg-zinc-700 rounded-full text-xs">
              {filter.count}
            </span>
          </button>
        ))}
      </div>
    </div>
  );
}

// --- Right Panel Component ---
function RightPanel() {
  return (
    <div className="space-y-4">
      {/* Today's Stats */}
      <div className="bg-white dark:bg-zinc-800 rounded-2xl p-6 border border-zinc-200 dark:border-zinc-700">
        <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100 mb-4">Today</h3>
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-sm text-zinc-600 dark:text-zinc-400">Highlights</span>
            <span className="font-semibold text-zinc-900 dark:text-zinc-100">12</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-zinc-600 dark:text-zinc-400">Sources</span>
            <span className="font-semibold text-zinc-900 dark:text-zinc-100">5</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-zinc-600 dark:text-zinc-400">AI Reviews</span>
            <span className="font-semibold text-zinc-900 dark:text-zinc-100">8</span>
          </div>
        </div>
      </div>

      {/* Review Progress */}
      <div className="bg-white dark:bg-zinc-800 rounded-2xl p-6 border border-zinc-200 dark:border-zinc-700">
        <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100 mb-4">Review Progress</h3>
        <div className="space-y-4">
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-zinc-600 dark:text-zinc-400">Spaced Repetition</span>
              <span className="text-sm font-medium text-zinc-900 dark:text-zinc-100">68%</span>
            </div>
            <div className="w-full bg-zinc-200 dark:bg-zinc-700 rounded-full h-2">
              <div className="bg-blue-500 h-2 rounded-full" style={{ width: "68%" }}></div>
            </div>
          </div>
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-zinc-600 dark:text-zinc-400">New Items</span>
              <span className="text-sm font-medium text-zinc-900 dark:text-zinc-100">32%</span>
            </div>
            <div className="w-full bg-zinc-200 dark:bg-zinc-700 rounded-full h-2">
              <div className="bg-green-500 h-2 rounded-full" style={{ width: "32%" }}></div>
            </div>
          </div>
        </div>
      </div>

      {/* System Status */}
      <div className="bg-white dark:bg-zinc-800 rounded-2xl p-6 border border-zinc-200 dark:border-zinc-700">
        <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100 mb-4">System</h3>
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span className="text-sm text-zinc-600 dark:text-zinc-400">Database</span>
            </div>
            <Badge className="bg-zinc-900/5 dark:bg-zinc-50/10 ring-zinc-300/40 text-zinc-700 dark:text-zinc-200">
              <Database className="h-3.5 w-3.5 me-1" /> PostgreSQL
            </Badge>
          </div>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span className="text-sm text-zinc-600 dark:text-zinc-400">Cache</span>
            </div>
            <Badge className="bg-zinc-900/5 dark:bg-zinc-50/10 ring-zinc-300/40 text-zinc-700 dark:text-zinc-200">
              Redis
            </Badge>
          </div>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span className="text-sm text-zinc-600 dark:text-zinc-400">API</span>
            </div>
            <Badge className="bg-zinc-900/5 dark:bg-zinc-50/10 ring-zinc-300/40 text-zinc-700 dark:text-zinc-200">
              <Globe className="h-3.5 w-3.5 me-1" /> API
            </Badge>
          </div>
        </div>
      </div>
    </div>
  );
}

// --- Sidebar Component ---
function Sidebar() {
  const [activeItem, setActiveItem] = useState("inbox");

  const menuItems = [
    { id: "inbox", label: "Inbox", icon: BookOpen, count: 24 },
    { id: "review", label: "Review", icon: CheckCircle2, count: 8 },
    { id: "search", label: "Search", icon: Search, count: 0 },
    { id: "sources", label: "Sources", icon: Globe, count: 12 },
    { id: "analytics", label: "Analytics", icon: BarChart3, count: 0 },
    { id: "settings", label: "Settings", icon: Settings, count: 0 }
  ];

  return (
    <aside className="w-64 bg-white dark:bg-zinc-900 border-r border-zinc-200 dark:border-zinc-800 p-6">
      <div className="space-y-6">
        {/* Logo */}
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
            <Zap className="h-5 w-5 text-white" />
          </div>
          <span className="text-xl font-bold text-zinc-900 dark:text-zinc-100">ZgrWise</span>
        </div>

        {/* Menu */}
        <nav className="space-y-1">
          {menuItems.map((item) => {
            const Icon = item.icon;
            return (
              <button
                key={item.id}
                onClick={() => setActiveItem(item.id)}
                className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 ${
                  activeItem === item.id
                    ? "bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-950/30 dark:to-purple-950/30 text-blue-700 dark:text-blue-300 shadow-sm"
                    : "text-zinc-600 dark:text-zinc-400 hover:bg-zinc-100 dark:hover:bg-zinc-800"
                }`}
              >
                <Icon className="h-4 w-4" />
                <span className="flex-1 text-left">{item.label}</span>
                {item.count > 0 && (
                  <span className="px-2 py-0.5 bg-zinc-200 dark:bg-zinc-700 rounded-full text-xs">
                    {item.count}
                  </span>
                )}
              </button>
            );
          })}
        </nav>

        {/* System Status */}
        <div className="pt-6 border-t border-zinc-200 dark:border-zinc-800">
          <div className="space-y-2">
            <Badge className="bg-zinc-900/5 dark:bg-zinc-50/10 ring-zinc-300/40 text-zinc-700 dark:text-zinc-200">
              <Globe className="h-3.5 w-3.5 me-1" /> API
            </Badge>
            <Badge className="bg-zinc-900/5 dark:bg-zinc-50/10 ring-zinc-300/40 text-zinc-700 dark:text-zinc-200">
              Redis
            </Badge>
          </div>
        </div>
      </div>
    </aside>
  );
}

// --- Main Component ---
export default function ZgrWiseUI() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-white to-zinc-50 dark:from-zinc-950 dark:to-zinc-900 text-zinc-900 dark:text-zinc-100">
      <div className="mx-auto max-w-7xl flex">
        <Sidebar />

        <main className="flex-1 p-4 md:p-6">
          <TopBar />

          <div className="mt-4 grid grid-cols-1 lg:grid-cols-[1fr,320px] xl:grid-cols-[1fr,360px] gap-5">
            {/* List */}
            <div className="flex flex-col gap-3">
              <HighlightCard
                title="Machine learning algorithms can be used to analyze large datasets and extract meaningful patterns…"
                excerpt="We explore supervised and unsupervised approaches for industrial data streams and propose a hybrid retrieval pipeline…"
                kind="Research Paper"
                author="Dr. Smith"
                ago="2 days ago"
                aiScore={0.892}
                tone="blue"
              />
              <HighlightCard
                title="The importance of data visualization in understanding complex information"
                excerpt="Good visualization practices help transform raw numbers into clear stories. This piece covers layout, hierarchies, and perceptual cues…"
                kind="Blog Post"
                author="Jane Doe"
                ago="1 week ago"
                textScore={0.756}
                tone="green"
              />
            </div>

            {/* Right Panel */}
            <RightPanel />
          </div>
        </main>
      </div>
    </div>
  );
}
