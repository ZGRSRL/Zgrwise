import './globals.css'
import { Inter } from 'next/font/google'
import { Providers } from './providers'

const inter = Inter({ subsets: ['latin'] })

export const metadata = {
  title: 'ZgrWise - Knowledge Management',
  description: 'Organize, search, and review your knowledge highlights',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="h-full">
      <body className={`${inter.className} h-full bg-[#FAFAFA] text-slate-800`}>
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  )
} 