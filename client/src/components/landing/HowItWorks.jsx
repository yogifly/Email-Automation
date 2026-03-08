import './HowItWorks.css'

const steps = [
  {
    num: '01',
    title: 'Connect Your Inbox',
    desc: 'Link your Gmail or any IMAP-compatible inbox securely in under 60 seconds. Zero data stored without your consent.',
    visual: '📨',
  },
  {
    num: '02',
    title: 'AI Learns Your Style',
    desc: 'BharatMail analyzes your past emails to understand tone, vocabulary, and your communication patterns across different contacts.',
    visual: '🧠',
  },
  {
    num: '03',
    title: 'Smart Inbox Activates',
    desc: 'Your landing transforms — emails are ranked, categorized, and ready for one-click AI replies. Reminders appear automatically.',
    visual: '✦',
  },
  {
    num: '04',
    title: 'You Stay in Control',
    desc: 'Review, edit, and send. BharatMail suggests — you decide. Every interaction trains your personal model to get smarter.',
    visual: '🎯',
  },
]

export default function HowItWorks() {
  return (
    <section className="hiw-section" id="how">
      <div className="hiw-inner">
        <div className="hiw-left">
          <span className="hiw-eyebrow">HOW IT WORKS</span>
          <h2 className="hiw-title">
            Up and running<br />
            <em>in minutes</em>
          </h2>
          <p className="hiw-body">
            No complex setup. No learning curve. BharatMail integrates with your
            existing workflow and starts delivering value from day one.
          </p>
          <div className="hiw-accent-box">
            <span className="hiw-accent-box__icon">⚡</span>
            <div>
              <div className="hiw-accent-box__title">Average Setup Time</div>
              <div className="hiw-accent-box__val">under 3 minutes</div>
            </div>
          </div>
        </div>

        <div className="hiw-right">
          {steps.map((step, i) => (
            <div className="hiw-step" key={step.num}>
              <div className="hiw-step__left">
                <div className="hiw-step__num">{step.num}</div>
                {i < steps.length - 1 && <div className="hiw-step__connector" />}
              </div>
              <div className="hiw-step__content">
                <div className="hiw-step__visual">{step.visual}</div>
                <div>
                  <h3 className="hiw-step__title">{step.title}</h3>
                  <p className="hiw-step__desc">{step.desc}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
