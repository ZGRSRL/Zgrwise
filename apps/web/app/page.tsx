import Sidebar from "@/components/Sidebar";
import FeedItem from "@/components/FeedItem";
import StatCard from "@/components/StatCard";
import { Input } from "@/components/ui/input";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/button";

export default function Page() {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-[240px_1fr_320px]">
      {/* Left: Sidebar */}
      <Sidebar />

      {/* Center: Feed */}
      <main className="min-h-[100dvh] px-4 lg:px-8 py-6">
        <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center">
          <div className="flex-1">
            <Input placeholder="Search your highlights, articles, and sources…" />
          </div>
          <div className="flex gap-2">
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline">All Content</Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem>All</DropdownMenuItem>
                <DropdownMenuItem>AI Matches</DropdownMenuItem>
                <DropdownMenuItem>Text Matches</DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline">All Sources</Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem>Web</DropdownMenuItem>
                <DropdownMenuItem>PDF</DropdownMenuItem>
                <DropdownMenuItem>YouTube</DropdownMenuItem>
                <DropdownMenuItem>RSS</DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline">All Time</Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem>Today</DropdownMenuItem>
                <DropdownMenuItem>This Week</DropdownMenuItem>
                <DropdownMenuItem>This Month</DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>

        <div className="space-y-3">
          <FeedItem
            type="paper"
            title="Machine learning algorithms can be used to analyze large datasets and extract meaningful patterns…"
            excerpt="We explore supervised and unsupervised approaches for industrial data streams and propose a hybrid retrieval pipeline…"
            source="Research Paper • Dr. Smith"
            timeAgo="2 days ago"
            scoreTag="AI Match 0.892"
          />
          <FeedItem
            type="web"
            title="The importance of data visualization in understanding complex information"
            excerpt="Good visualization practices help transform raw numbers into clear stories. This piece covers layout, hierarchies, and perceptual cues…"
            source="Blog Post • Jane Doe"
            timeAgo="1 week ago"
            scoreTag="Text Match 0.756"
          />
          {/* TODO: gerçek veriye bağla */}
        </div>
      </main>

      {/* Right: Stats */}
      <aside className="hidden lg:block border-l bg-white/70 backdrop-blur p-6 space-y-3">
        <StatCard title="Today" value="12 Highlights" hint="3 new RSS items" />
        <StatCard title="Review Progress" value="24%" hint="Spaced repetition" />
        <StatCard title="System" value="All Good" hint="API • DB • Redis" />
      </aside>
    </div>
  );
}