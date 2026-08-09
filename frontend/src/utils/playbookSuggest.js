// Lightweight keyword heuristic to auto-suggest which org playbook profile is
// most relevant to the pasted content -- a *suggestion*, not a decision. The
// user can always override it manually; a manual choice always wins.
const SIGNALS = [
  { profile: 'healthcare', keywords: ['patient', 'diagnosis', 'hipaa', 'medical_record', 'phi', 'icd-10', 'clinician'] },
  { profile: 'fintech', keywords: ['card_number', 'payment', 'transaction', 'stripe', 'paypal', 'checkout', 'invoice', 'cvv'] },
  { profile: 'enterprise', keywords: ['pci-dss', 'pci dss', 'mfa', 'privileged', 'admin_role', 'audit_trail'] },
  { profile: 'startup', keywords: ['owasp', 'mvp', 'startup'] },
];

export function suggestPlaybookProfile(content) {
  if (!content || content.trim().length < 8) return null;
  const text = content.toLowerCase();

  let best = null;
  let bestScore = 0;
  for (const { profile, keywords } of SIGNALS) {
    const score = keywords.reduce((n, kw) => n + (text.includes(kw) ? 1 : 0), 0);
    if (score > bestScore) {
      bestScore = score;
      best = profile;
    }
  }
  return best; // null if no signal found -- don't force a guess
}
