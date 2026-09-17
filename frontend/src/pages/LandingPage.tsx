import { Link } from 'react-router-dom';
import {
  Sprout,
  Microscope,
  BookOpen,
  MessageSquare,
  Lightbulb,
  Leaf,
  TrendingUp,
  ShieldCheck,
  ArrowRight,
  Globe,
  Beaker,
  Database,
} from 'lucide-react';
import { Logo } from '@/components/shared/Logo';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

const features = [
  {
    icon: Microscope,
    title: 'Evidence-Grounded Analysis',
    description:
      'Multi-factor environmental assessment across soil, climate, land, biodiversity, and human impact — every conclusion traced to scientific evidence.',
  },
  {
    icon: MessageSquare,
    title: 'Conversational Reasoning',
    description:
      'Ask questions in plain language. TerraSage maintains environmental context across turns and surfaces missing information when it matters.',
  },
  {
    icon: Lightbulb,
    title: 'Actionable Recommendations',
    description:
      'Prioritized recommendations with expected impact, time horizon, confidence level, and the evidence supporting each one.',
  },
  {
    icon: BookOpen,
    title: 'Evidence Library',
    description:
      'A searchable library of peer-reviewed studies, government reports, and datasets — every source cited and traceable.',
  },
];

const metrics = [
  { label: 'Environmental metrics tracked', value: '25+', icon: Leaf },
  { label: 'Evidence sources', value: '1,200+', icon: BookOpen },
  { label: 'Recommendation confidence', value: '90%+', icon: ShieldCheck },
  { label: 'Reasoning transparency', value: '100%', icon: TrendingUp },
];

const categories = [
  { icon: Beaker, label: 'Soil', desc: 'pH, organic carbon, moisture, nutrients' },
  { icon: Globe, label: 'Climate', desc: 'Rainfall, temperature, humidity' },
  { icon: Leaf, label: 'Land', desc: 'Land use, cover, erosion risk' },
  { icon: Sprout, label: 'Biodiversity', desc: 'Species richness, habitat diversity' },
  { icon: ShieldCheck, label: 'Human Impact', desc: 'Pollution, deforestation, water stress' },
];

export function LandingPage() {
  return (
    <div className="min-h-screen bg-background">
      {/* Nav */}
      <header className="sticky top-0 z-40 border-b border-border bg-background/80 backdrop-blur-md">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4 sm:px-6">
          <Logo size="md" />
          <nav className="hidden items-center gap-6 sm:flex">
            <a href="#features" className="text-sm font-medium text-muted-foreground hover:text-foreground">
              Features
            </a>
            <a href="#how-it-works" className="text-sm font-medium text-muted-foreground hover:text-foreground">
              How it works
            </a>
            <a href="#evidence" className="text-sm font-medium text-muted-foreground hover:text-foreground">
              Evidence
            </a>
          </nav>
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="sm" asChild>
              <Link to="/login">Log in</Link>
            </Button>
            <Button size="sm" asChild>
              <Link to="/signup">Get started</Link>
            </Button>
          </div>
        </div>
      </header>

      {/* Hero */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-primary/5 to-transparent" />
        <div className="relative mx-auto max-w-6xl px-4 py-20 sm:px-6 lg:py-28">
          <div className="mx-auto max-w-3xl text-center">
            <Badge variant="outline" className="mb-6 border-primary/20 bg-primary/5 text-primary">
              <Sprout className="mr-1.5 h-3 w-3" />
              AI Environmental Intelligence
            </Badge>
            <h1 className="font-display text-4xl font-bold leading-tight text-foreground sm:text-5xl lg:text-6xl text-balance">
              An evidence-grounded AI environmental scientist
            </h1>
            <p className="mt-6 text-lg leading-relaxed text-muted-foreground text-balance">
              TerraSage analyzes soil, climate, land, biodiversity, and human impact to deliver
              actionable recommendations — every conclusion backed by scientific evidence.
            </p>
            <div className="mt-8 flex flex-col items-center justify-center gap-3 sm:flex-row">
              <Button size="lg" asChild>
                <Link to="/signup">
                  Start analyzing
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
              <Button variant="outline" size="lg" asChild>
                <Link to="/login">View demo dashboard</Link>
              </Button>
            </div>
            <p className="mt-4 text-xs text-muted-foreground">
              No credit card required · Demo data available immediately
            </p>
          </div>
        </div>
      </section>

      {/* Metrics */}
      <section className="border-y border-border bg-card/50">
        <div className="mx-auto grid max-w-6xl grid-cols-2 gap-6 px-4 py-12 sm:px-6 lg:grid-cols-4">
          {metrics.map((m) => {
            const Icon = m.icon;
            return (
              <div key={m.label} className="text-center">
                <Icon className="mx-auto mb-2 h-6 w-6 text-primary" />
                <div className="font-display text-3xl font-bold text-foreground">{m.value}</div>
                <div className="mt-1 text-sm text-muted-foreground">{m.label}</div>
              </div>
            );
          })}
        </div>
      </section>

      {/* Features */}
      <section id="features" className="mx-auto max-w-6xl px-4 py-20 sm:px-6">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="font-display text-3xl font-bold text-foreground sm:text-4xl">
            Not a chatbot. A scientist.
          </h2>
          <p className="mt-4 text-muted-foreground">
            TerraSage reasons across environmental domains, surfaces missing information,
            and traces every recommendation to peer-reviewed evidence.
          </p>
        </div>
        <div className="mt-12 grid gap-6 sm:grid-cols-2">
          {features.map((f) => {
            const Icon = f.icon;
            return (
              <Card key={f.title} className="border-border transition-shadow hover:shadow-md">
                <CardContent className="p-6">
                  <div className="flex h-11 w-11 items-center justify-center rounded-lg bg-primary/10">
                    <Icon className="h-5 w-5 text-primary" />
                  </div>
                  <h3 className="mt-4 font-display text-lg font-semibold text-foreground">
                    {f.title}
                  </h3>
                  <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
                    {f.description}
                  </p>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </section>

      {/* How it works */}
      <section id="how-it-works" className="border-y border-border bg-card/50">
        <div className="mx-auto max-w-6xl px-4 py-20 sm:px-6">
          <div className="mx-auto max-w-2xl text-center">
            <h2 className="font-display text-3xl font-bold text-foreground sm:text-4xl">
              How TerraSage works
            </h2>
            <p className="mt-4 text-muted-foreground">
              From raw environmental data to evidence-backed action plans.
            </p>
          </div>
          <div className="mt-12 grid gap-6 md:grid-cols-3">
            {[
              {
                step: '01',
                title: 'Input environmental data',
                description:
                  'Describe your site in natural language or enter structured data across soil, climate, land, biodiversity, and human impact.',
              },
              {
                step: '02',
                title: 'AI reasoning & evidence retrieval',
                description:
                  'TerraSage analyzes cross-domain relationships, retrieves relevant evidence, and identifies missing information that would improve confidence.',
              },
              {
                step: '03',
                title: 'Act on recommendations',
                description:
                  'Receive prioritized recommendations with expected impact, time horizon, confidence, and the scientific evidence behind each one.',
              },
            ].map((s) => (
              <div key={s.step} className="relative">
                <span className="font-display text-5xl font-bold text-primary/15">{s.step}</span>
                <h3 className="mt-2 font-display text-lg font-semibold text-foreground">{s.title}</h3>
                <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{s.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Categories */}
      <section id="evidence" className="mx-auto max-w-6xl px-4 py-20 sm:px-6">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="font-display text-3xl font-bold text-foreground sm:text-4xl">
            Five environmental domains, one analysis
          </h2>
          <p className="mt-4 text-muted-foreground">
            TerraSage evaluates the full environmental picture, not isolated metrics.
          </p>
        </div>
        <div className="mt-12 grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
          {categories.map((c) => {
            const Icon = c.icon;
            return (
              <Card key={c.label} className="text-center">
                <CardContent className="flex flex-col items-center p-5">
                  <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
                    <Icon className="h-6 w-6 text-primary" />
                  </div>
                  <h3 className="mt-3 font-semibold text-foreground">{c.label}</h3>
                  <p className="mt-1 text-xs text-muted-foreground">{c.desc}</p>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </section>

      {/* CTA */}
      <section className="border-t border-border bg-primary">
        <div className="mx-auto max-w-6xl px-4 py-20 text-center sm:px-6">
          <Database className="mx-auto h-10 w-10 text-primary-foreground/80" />
          <h2 className="mt-4 font-display text-3xl font-bold text-primary-foreground sm:text-4xl">
            Start your environmental analysis
          </h2>
          <p className="mx-auto mt-4 max-w-xl text-primary-foreground/80">
            Join environmental scientists using TerraSage to make evidence-backed decisions.
          </p>
          <div className="mt-8 flex flex-col items-center justify-center gap-3 sm:flex-row">
            <Button size="lg" variant="secondary" asChild>
              <Link to="/signup">
                Create account
                <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
            <Button
              size="lg"
              variant="outline"
              className="border-primary-foreground/30 bg-transparent text-primary-foreground hover:bg-primary-foreground/10 hover:text-primary-foreground"
              asChild
            >
              <Link to="/login">Log in</Link>
            </Button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border bg-card/50">
        <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-4 px-4 py-8 sm:flex-row sm:px-6">
          <Logo size="sm" />
          <p className="text-xs text-muted-foreground">
            © 2026 TerraSage. Demo data — not for production use.
          </p>
        </div>
      </footer>
    </div>
  );
}
