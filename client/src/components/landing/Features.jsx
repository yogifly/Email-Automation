import './Features.css'

const features = [
  {
    id: '01',
    icon: '⚡',
    title: 'Smart Prioritization',
    desc: 'AI scans every incoming email and ranks by urgency, sender importance, and deadline proximity. Critical messages rise to the top instantly.',
    tag: 'Core AI',
    color: 'saffron',
  },
  {
    id: '02',
    icon: '✍️',
    title: 'Context-Aware Replies',
    desc: 'Generate precise, professional replies that match your tone and history with each sender. One click drafts, you approve.',
    tag: 'Generative AI',
    color: 'teal',
  },
  {
    id: '03',
    icon: '🔔',
    title: 'Intelligent Reminders',
    desc: 'Never forget a critical thread. BharatMail nudges you on unread, unresponded emails and flags time-sensitive follow-ups automatically.',
    tag: 'Automation',
    color: 'gold',
  },
  {
    id: '04',
    icon: '🎯',
    title: 'Adaptive Style Learning',
    desc: 'The assistant learns your vocabulary, formality level, and communication habits — and gets sharper with every interaction.',
    tag: 'Machine Learning',
    color: 'saffron',
  },
  {
    id: '05',
    icon: '🗂️',
    title: 'Intelligent Categorization',
    desc: 'Emails auto-sort into dynamic categories: clients, ops, newsletters, alerts. Your inbox becomes a clean, structured workspace.',
    tag: 'Organization',
    color: 'teal',
  },
  {
    id: '06',
    icon: '🛡️',
    title: 'Privacy-First Design',
    desc: 'End-to-end encrypted. Your data is never sold or used for external model training. Built for professionals who value security.',
    tag: 'Security',
    color: 'gold',
  },
]

export default function Features() {
  return (
    <section className="feat-section" id="features">
      <div className="feat-header">
        <span className="feat-eyebrow">CAPABILITIES</span>
        <h2 className="feat-title">
          Everything your inbox<br />
          <em>should have been</em>
        </h2>
        <p className="feat-subtitle">
          Six pillars of intelligent email management — engineered to reclaim your time.
        </p>
      </div>

      <div className="feat-grid">
        {features.map((f) => (
          <div className={`feat-card feat-card--${f.color}`} key={f.id}>
            <div className="feat-card__top">
              <span className="feat-card__id">{f.id}</span>
              <span className="feat-card__tag">{f.tag}</span>
            </div>
            <div className="feat-card__icon">{f.icon}</div>
            <h3 className="feat-card__title">{f.title}</h3>
            <p className="feat-card__desc">{f.desc}</p>
            <div className="feat-card__line" />
          </div>
        ))}
      </div>
    </section>
  )
}
