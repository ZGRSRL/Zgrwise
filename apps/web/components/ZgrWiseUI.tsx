import { useMemo, useState } from "react";
import {
  Inbox,
  Search,
  CheckSquare,
  Rss,
  BarChart3,
  Settings,
  ChevronDown,
  Sparkles,
  Clock,
  CheckCircle2,
  Database,
  Globe,
  BookText,
  ChevronRight,
  Flame,
  BookOpen,
  CircleDot,
} from "lucide-react";

/**
 * ZgrWise – Inbox + Search + Review + RSS + KPI Right Panel
 * TailwindCSS only. Drop-in demo for Next.js (App or Pages Router)
 */

// === Atoms ===
function Badge({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ring-1 ring-inset ${className}`} />
  );
}

function Pill({ active, children, onClick }: { active?: boolean; children: React.ReactNode; onClick?: () => void }) {
  return (
    <button
      onClick={onClick}
      className={`inline-flex items-center gap-1 rounded-full px-3 py-1 text-sm border transition hover:shadow-sm ${
        active
          ? "bg-blue-600 text-white border-blue-600"
          : "bg-white/70 dark:bg-zinc-800/70 border-zinc-200 dark:border-zinc-700 text-zinc-700 dark:text-zinc-200"
      }`}
    >
      {children}
    </button>
  );
}

function Progress({ value }: { value: number }) {
  return (
    <div className="w-full h-2 rounded-full bg-zinc-200 dark:bg-zinc-800 overflow-hidden">
      <div className="h-full bg-emerald-500 transition-all" style={{ width: `${Math.min(100, Math.max(0, value))}%` }} />
    </div>
  );
}

// === Sidebar ===
function Sidebar({ active, onChange }: { active: string; onChange: (v: string) => void }) {
  const items = [
    { label: "Inbox", icon: Inbox },
    { label: "Search", icon: Search },
    { label: "Review", icon: CheckSquare },
    { label: "RSS", icon: Rss },
    { label: "Analytics", icon: BarChart3 },
    { label: "Settings", icon: Settings },
  ];

  return (
    <aside className="hidden md:flex md:w-64 shrink-0 border-r border-zinc-200 dark:border-zinc-800 bg-white/70 dark:bg-zinc-950/50 backdrop-blur-sm">
      <div className="w-full p-4">
        <div className="flex items-center gap-2 mb-6">
          <div className="h-9 w-9 rounded-2xl bg-blue-600 text-white grid place-items-center font-semibold">Z</div>
          <div className="text-lg font-semibold">ZgrWise</div>
        </div>
        <nav className="flex flex-col gap-1">
          {items.map(({ label, icon: Icon }) => {
            const isActive = label === active;
            return (
              <button
                key={label}
                onClick={() => onChange(label)}
                className={`group flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm transition w-full text-left ${
                  isActive
                    ? "bg-gradient-to-r from-blue-600/90 to-indigo-600/90 text-white shadow-sm"
                    : "text-zinc-700 dark:text-zinc-200 hover:bg-zinc-100 dark:hover:bg-zinc-900"
                }`}
              >
                <Icon className={`h-4 w-4 ${isActive ? "opacity-100" : "opacity-80"}`} />
                <span className="font-medium">{label}</span>
              </button>
            );
          })}
        </nav>
      </div>
    </aside>
  );
}

// === TopBar ===
function TopBar({ right }: { right?: React.ReactNode }) {
  const [query, setQuery] = useState("");
  return (
    <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
      <div className="flex-1">
        <div className="relative">
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search your highlights, articles, and sources…"
            className="w-full rounded-2xl border border-zinc-200 dark:border-zinc-800 bg-white/80 dark:bg-zinc-950/40 px-5 py-3 pe-12 outline-none focus:ring-2 focus:ring-blue-500/60"
          />
          <Search className="h-5 w-5 absolute right-4 top-1/2 -translate-y-1/2 text-zinc-400" />
        </div>
      </div>
      <div className="flex items-center gap-2">{right}</div>
    </div>
  );
}

// === Highlight Card (Inbox) ===
function HighlightCard({
  title,
  excerpt,
  kind = "Research Paper",
  author = "",
  ago = "",
  aiScore,
  textScore,
  tone = "blue",
}: {
  title: string;
  excerpt: string;
  kind?: string;
  author?: string;
  ago?: string;
  aiScore?: number;
  textScore?: number;
  tone?: "blue" | "green";
}) {
  const toneMap: Record<string, string> = {
    blue: "border-blue-200/60 dark:border-blue-900/40 bg-blue-50/70 dark:bg-blue-950/20",
    green: "border-emerald-200/60 dark:border-emerald-900/40 bg-emerald-50/70 dark:bg-emerald-950/20",
  };

  return (
    <div className={`relative rounded-2xl border p-4 md:p-5 shadow-sm hover:shadow-md transition ${toneMap[tone]}`}>
      <div className="absolute right-3 top-3 flex gap-2">
        {typeof aiScore === "number" && (
          <Badge className="bg-blue-600/10 text-blue-700 dark:text-blue-300 ring-blue-300/40">
            <Sparkles className="h-3.5 w-3.5 me-1" /> AI Match {aiScore.toFixed(3)}
          </Badge>
        )}
        {typeof textScore === "number" && (
          <Badge className="bg-emerald-600/10 text-emerald-700 dark:text-emerald-300 ring-emerald-300/40">
            <BookText className="h-3.5 w-3.5 me-1" /> Text Match {textScore.toFixed(3)}
          </Badge>
        )}
      </div>

      <h3 className="text-zinc-900 dark:text-zinc-50 font-semibold text-lg md:text-xl pr-36">{title}</h3>
      <p className="text-zinc-600 dark:text-zinc-300 mt-1 line-clamp-2">{excerpt}</p>

      <div className="flex items-center gap-2 mt-3 text-sm text-zinc-500 dark:text-zinc-400">
        <Badge className="bg-zinc-900/5 dark:bg-zinc-50/10 ring-zinc-300/40 text-zinc-700 dark:text-zinc-200">{kind}</Badge>
        {author && <span>• {author}</span>}
        {ago && (
          <span className="inline-flex items-center gap-1">
            <Clock className="h-3.5 w-3.5" /> {ago}
          </span>
        )}
      </div>
    </div>
  );
}

// === Review Card (Spaced Repetition) ===
function ReviewCard({ title, excerpt, dueToday, difficulty, nextIn }: { title: string; excerpt: string; dueToday?: boolean; difficulty?: "easy" | "med" | "hard"; nextIn?: string; }) {
  const diffToColor: Record<string, string> = {
    easy: "bg-emerald-500",
    med: "bg-amber-500",
    hard: "bg-rose-500",
  };
  return (
    <div className="rounded-2xl border border-zinc-200 dark:border-zinc-800 bg-white/80 dark:bg-zinc-950/50 p-5 shadow-sm">
      <div className="flex items-start justify-between gap-3">
        <div>
          <h3 className="text-lg font-semibold">{title}</h3>
          <p className="text-zinc-600 dark:text-zinc-300 mt-1 line-clamp-2">{excerpt}</p>
          <div className="mt-3 flex items-center gap-2 text-sm text-zinc-500">
            {dueToday && (
              <Badge className="bg-blue-600/10 text-blue-700 dark:text-blue-300 ring-blue-300/40">
                <Flame className="h-3.5 w-3.5 me-1" /> Due today
              </Badge>
            )}
            {difficulty && <span className={`inline-flex items-center gap-1 ${diffToColor[difficulty]} text-white rounded-full px-2.5 py-0.5 text-xs`}>
              <CircleDot className="h-3.5 w-3.5" /> {difficulty}
            </span>}
            {nextIn && (
              <span className="inline-flex items-center gap-1"><Clock className="h-3.5 w-3.5" /> Next in {nextIn}</span>
            )}
          </div>
        </div>
        <BookOpen className="h-6 w-6 text-zinc-400" />
      </div>
      <div className="mt-4 grid grid-cols-4 gap-2">
        {[
          { label: "Again", cls: "bg-rose-600 hover:bg-rose-700" },
          { label: "Hard", cls: "bg-amber-600 hover:bg-amber-700" },
          { label: "Good", cls: "bg-blue-600 hover:bg-blue-700" },
          { label: "Easy", cls: "bg-emerald-600 hover:bg-emerald-700" },
        ].map((b) => (
          <button key={b.label} className={`text-white rounded-xl px-3 py-2 text-sm font-medium transition ${b.cls}`}>{b.label}</button>
        ))}
      </div>
    </div>
  );
}

// === RSS List ===
function RSSRow({ name, url, unread, last }: { name: string; url: string; unread?: number; last?: string }) {
  return (
    <div className="flex items-center justify-between p-3 rounded-xl border border-zinc-200 dark:border-zinc-800 bg-white/70 dark:bg-zinc-950/40 hover:shadow-sm transition">
      <div className="flex items-center gap-3">
        <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-indigo-500 to-blue-500 grid place-items-center text-white text-sm font-semibold">
          {name.slice(0, 1).toUpperCase()}
        </div>
        <div>
          <div className="font-medium">{name}</div>
          <div className="text-xs text-zinc-500 truncate max-w-[260px]">{url}</div>
        </div>
      </div>
      <div className="flex items-center gap-3">
        {typeof unread === "number" && (
          <Badge className="bg-emerald-600/10 text-emerald-700 dark:text-emerald-300 ring-emerald-300/40">{unread} unread</Badge>
        )}
        <div className="text-xs text-zinc-500">{last}</div>
        <ChevronRight className="h-4 w-4 text-zinc-400" />
      </div>
    </div>
  );
}

// === Search Results (with query highlight) ===
function highlight(text: string, q: string) {
  if (!q) return text;
  try {
    const parts = text.split(new RegExp(`(${q.replace(/[-/\^$*+?.()|[\]{}]/g, "\$&")})`, "ig"));
    return parts.map((p, i) =>
      //i.test(q) && p.toLowerCase() === q.toLowerCase() ? (
        <mark key={i} className="bg-yellow-200 px-0.5 rounded">{p}</mark>
      ) : (
        <span key={i}>{p}</span>
      )
    );
  } catch {
    return text;
  }
}

function SearchResultCard({ title, excerpt, source, score, query }: { title: string; excerpt: string; source: string; score?: number; query: string }) {
  return (
    <div className="rounded-2xl border border-zinc-200 dark:border-zinc-800 bg-white/80 dark:bg-zinc-950/50 p-4 shadow-sm hover:shadow-md transition">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold pr-20">{highlight(title, query)}</h3>
        {typeof score === "number" && (
          <Badge className="bg-indigo-600/10 text-indigo-700 dark:text-indigo-300 ring-indigo-300/40">
            <Sparkles className="h-3.5 w-3.5 me-1" /> {score.toFixed(3)}
          </Badge>
        )}
      </div>
      <p className="text-zinc-600 dark:text-zinc-300 mt-1 line-clamp-2">{highlight(excerpt, query)}</p>
      <div className="mt-2 text-sm text-zinc-500">{source}</div>
    </div>
  );
}

// === Right KPI Panel ===
function RightPanel() {
  return (
    <aside className="w-full md:w-80 lg:w-88 xl:w-96 shrink-0">
      <div className="flex flex-col gap-4">
        <div className="rounded-2xl border border-zinc-200 dark:border-zinc-800 bg-white/80 dark:bg-zinc-950/50 p-4 shadow-sm">
          <div className="text-sm text-zinc-500 mb-1">TODAY</div>
          <div className="flex items-end justify-between">
            <div>
              <div className="text-3xl font-semibold">12</div>
              <div className="text-zinc-500">Highlights</div>
            </div>
            <Badge className="bg-indigo-600/10 text-indigo-700 dark:text-indigo-300 ring-indigo-300/40">
              <Rss className="h-3.5 w-3.5 me-1" /> 3 new RSS
            </Badge>
          </div>
        </div>

        <div className="rounded-2xl border border-zinc-200 dark:border-zinc-800 bg-white/80 dark:bg-zinc-950/50 p-4 shadow-sm">
          <div className="flex items-center justify-between mb-3">
            <div className="text-sm text-zinc-500">REVIEW PROGRESS</div>
            <Badge className="bg-emerald-600/10 text-emerald-700 dark:text-emerald-300 ring-emerald-300/40">24%</Badge>
          </div>
          <Progress value={24} />
          <div className="mt-2 text-sm text-zinc-500">Spaced repetition</div>
        </div>

        <div className="rounded-2xl border border-zinc-200 dark:border-zinc-800 bg-white/80 dark:bg-zinc-950/50 p-4 shadow-sm">
          <div className="text-sm text-zinc-500 mb-2">SYSTEM</div>
          <div className="flex items-center gap-2">
            <CheckCircle2 className="h-5 w-5 text-emerald-500" />
            <div className="font-medium">All Good</div>
          </div>
          <div className="mt-3 flex flex-wrap gap-2">
            <Badge className="bg-zinc-900/5 dark:bg-zinc-50/10 ring-zinc-300/40 text-zinc-700 dark:text-zinc-200">
              <Database className="h-3.5 w-3.5 me-1" /> DB
            </Badge>
            <Badge className="bg-zinc-900/5 dark:bg-zinc-50/10 ring-zinc-300/40 text-zinc-700 dark:text-zinc-200">
              <Globe className="h-3.5 w-3.5 me-1" /> API
            </Badge>
            <Badge className="bg-zinc-900/5 dark:bg-zinc-50/10 ring-zinc-300/40 text-zinc-700 dark:text-zinc-200">Redis</Badge>
          </div>
        </div>
      </div>
    </aside>
  );
}

// === Page Panels ===
function InboxPanel() {
  return (
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
  );
}

function ReviewPanel() {
  return (
    <div className="flex flex-col gap-3">
      <ReviewCard
        title="What is vector similarity search?"
        excerpt="Vector databases store embeddings; similarity search compares vectors via metrics like cosine or dot product."
        dueToday
        difficulty="med"
        nextIn="4h"
      />
      <ReviewCard
        title="Pros & cons of FAISS vs. pgvector"
        excerpt="FAISS excels at brute-force and IVF/Flat indices on GPU; pgvector is simpler for transactional + SQL workflows."
        difficulty="hard"
        nextIn="2d"
      />
    </div>
  );
}

function RSSPanel() {
  return (
    <div className="flex flex-col gap-3">
      <RSSRow name="Sebastian Raschka" url="https://magazine.sebastianraschka.com/rss" unread={5} last="2h ago" />
      <RSSRow name="ACM Queue" url="https://queue.acm.org/rss/feeds/queuecontent.xml" unread={1} last="8h ago" />
      <RSSRow name="arXiv AI" url="https://arxiv.org/rss/cs.AI" unread={12} last="1d ago" />
    </div>
  );
}

function SearchPanel() {
  const [q, setQ] = useState("retrieval");
  const right = (
    <>
      <Pill active>All Content <ChevronDown className="h-4 w-4" /></Pill>
      <Pill>All Sources <ChevronDown className="h-4 w-4" /></Pill>
      <Pill>All Time <ChevronDown className="h-4 w-4" /></Pill>
    </>
  );
  return (
    <>
      <TopBar right={right} />
      <div className="mt-4 grid gap-3">
        <SearchResultCard
          title="A hybrid retrieval pipeline combining BM25 and dense retrieval"
          excerpt="We propose staged retrieval where sparse terms recall is followed by neural reranking for improved retrieval precision."
          source="Web • Research Blog"
          score={0.834}
          query={q}
        />
        <SearchResultCard
          title="Practical notes on retrieval for RAG systems"
          excerpt="Key choices include chunking, embedding model, vector store, index type, and cross-encoder reranking."
          source="PDF • Notes"
          score={0.782}
          query={q}
        />
      </div>
    </>
  );
}

// === Main ===
export default function ZgrWiseUI() {
  const [active, setActive] = useState("Inbox");
  const rightDefault = (
    <>
      <Pill active>All Content <ChevronDown className="h-4 w-4" /></Pill>
      <Pill>All Sources <ChevronDown className="h-4 w-4" /></Pill>
      <Pill>All Time <ChevronDown className="h-4 w-4" /></Pill>
    </>
  );

  const mainPanel = useMemo(() => {
    if (active === "Review") return <ReviewPanel />;
    if (active === "RSS") return <RSSPanel />;
    if (active === "Search") return <SearchPanel />;
    return <InboxPanel />;
  }, [active]);

  return (
    <div className="min-h-screen bg-gradient-to-b from-white to-zinc-50 dark:from-zinc-950 dark:to-zinc-900 text-zinc-900 dark:text-zinc-100">
      <div className="mx-auto max-w-7xl flex">
        <Sidebar active={active} onChange={setActive} />

        <main className="flex-1 p-4 md:p-6">
          {active !== "Search" && <TopBar right={rightDefault} />}

          <div className="mt-4 grid grid-cols-1 lg:grid-cols-[1fr,320px] xl:grid-cols-[1fr,360px] gap-5">
            <div>{mainPanel}</div>
            <RightPanel />
          </div>
        </main>
      </div>
    </div>
  );
}
