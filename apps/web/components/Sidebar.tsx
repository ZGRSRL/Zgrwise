'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { 
  Home, 
  Search, 
  BookOpen, 
  Rss, 
  Brain, 
  Settings,
  BarChart3,
  FileText
} from 'lucide-react'

const navigation = [
  { name: 'Inbox', href: '/', icon: Home },
  { name: 'Search', href: '/search', icon: Search },
  { name: 'Review', href: '/ai-review', icon: Brain },
  { name: 'RSS', href: '/rss', icon: Rss },
  { name: 'Analytics', href: '/analytics', icon: BarChart3 },
  { name: 'Settings', href: '/settings', icon: Settings },
]

export default function Sidebar() {
  const pathname = usePathname()

  return (
    <div className="flex h-full flex-col bg-white border-r border-gray-200">
      {/* Logo */}
      <div className="flex h-16 shrink-0 items-center px-6">
        <div className="flex items-center gap-2">
          <div className="h-8 w-8 rounded-lg bg-blue-600 flex items-center justify-center">
            <FileText className="h-5 w-5 text-white" />
          </div>
          <span className="text-xl font-semibold text-gray-900">ZgrWise</span>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex flex-1 flex-col px-4 py-4">
        <ul role="list" className="flex flex-1 flex-col gap-y-2">
          {navigation.map((item) => {
            const isActive = pathname === item.href
            return (
              <li key={item.name}>
                <Link
                  href={item.href}
                  className={`group flex gap-x-3 rounded-md p-3 text-sm font-medium leading-6 transition-colors ${
                    isActive
                      ? 'bg-blue-50 text-blue-700 border-r-2 border-blue-700'
                      : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'
                  }`}
                >
                  <item.icon
                    className={`h-5 w-5 shrink-0 ${
                      isActive ? 'text-blue-700' : 'text-gray-400 group-hover:text-gray-500'
                    }`}
                    aria-hidden="true"
                  />
                  {item.name}
                </Link>
              </li>
            )
          })}
        </ul>

        {/* Bottom section */}
        <div className="mt-auto border-t border-gray-200 pt-4">
          <div className="px-3 py-2">
            <div className="text-xs text-gray-500 mb-1">System Status</div>
            <div className="flex items-center gap-2">
              <div className="h-2 w-2 rounded-full bg-green-500"></div>
              <span className="text-xs text-gray-600">All systems operational</span>
            </div>
          </div>
        </div>
      </nav>
    </div>
  )
}