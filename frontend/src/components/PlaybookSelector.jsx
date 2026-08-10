import React, { useState, useEffect, useRef } from 'react';
import { ShieldCheck, ChevronDown, Plus, X, Sparkles } from 'lucide-react';
import { suggestPlaybookProfile } from '../utils/playbookSuggest';

export default function PlaybookSelector({ profile, setProfile, customRules, setCustomRules, content }) {
  const [profiles, setProfiles] = useState([]);
  const [showCustomForm, setShowCustomForm] = useState(false);
  const [draftTitle, setDraftTitle] = useState('');
  const [draftPatterns, setDraftPatterns] = useState('');
  const [draftFix, setDraftFix] = useState('');
  const [isAutoSuggested, setIsAutoSuggested] = useState(false);
  const [loadError, setLoadError] = useState(false);
  const manuallyChosen = useRef(false);

  useEffect(() => {
    fetch('/api/playbook-profiles')
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then((data) => { setProfiles(data.profiles || []); setLoadError(false); })
      .catch(() => { setProfiles([]); setLoadError(true); });
  }, []);

  // Auto-detect the most relevant org profile from pasted content -- only while
  // the user hasn't made an explicit choice themselves. A manual pick always wins.
  useEffect(() => {
    if (manuallyChosen.current) return;
    const suggestion = suggestPlaybookProfile(content);
    if (suggestion && suggestion !== profile) {
      setProfile(suggestion);
      setIsAutoSuggested(true);
    } else if (!suggestion && isAutoSuggested) {
      setProfile('');
      setIsAutoSuggested(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [content]);

  const handleManualSelect = (value) => {
    manuallyChosen.current = true;
    setIsAutoSuggested(false);
    setProfile(value);
  };

  const addCustomRule = () => {
    if (!draftTitle.trim() || !draftPatterns.trim()) return;
    setCustomRules([...customRules, {
      title: draftTitle.trim(),
      bad_patterns: draftPatterns,
      fix_hint: draftFix.trim(),
    }]);
    setDraftTitle('');
    setDraftPatterns('');
    setDraftFix('');
  };

  const removeCustomRule = (idx) => {
    setCustomRules(customRules.filter((_, i) => i !== idx));
  };

  const activeProfile = profiles.find((p) => p.id === profile);

  return (
    <div className="card" style={{ padding: '24px', marginBottom: '24px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '12px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{
            width: '32px', height: '32px', borderRadius: '8px',
            background: 'rgba(129, 140, 248, 0.15)', display: 'flex',
            alignItems: 'center', justifyContent: 'center', color: '#818cf8', flexShrink: 0
          }}>
            <ShieldCheck size={18} />
          </div>
          <div>
            <div className="label" style={{ marginBottom: '2px' }}>JUDEX PLAYBOOK</div>
            <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
              Store your org's security rules once — every future audit checks against them automatically.
            </div>
          </div>
        </div>

        <div style={{ minWidth: '260px' }}>
          <div style={{ position: 'relative' }}>
            <select
              className="custom-select"
              value={profile}
              onChange={(e) => handleManualSelect(e.target.value)}
              style={{ height: '38px' }}
            >
              <option value="">No playbook (standard audit)</option>
              {profiles.map((p) => (
                <option key={p.id} value={p.id}>{p.name} — {p.rule_count} rules</option>
              ))}
            </select>
            <ChevronDown size={15} style={{ position: 'absolute', right: '12px', top: '50%', transform: 'translateY(-50%)', pointerEvents: 'none', color: 'var(--text-muted)' }} />
          </div>
        </div>
      </div>

      {activeProfile && (
        <div style={{ fontSize: '11px', color: 'var(--text-faint)', marginTop: '10px', fontFamily: 'JetBrains Mono, monospace', display: 'flex', alignItems: 'center', gap: '6px' }}>
          {isAutoSuggested && (
            <span style={{
              display: 'inline-flex', alignItems: 'center', gap: '4px',
              color: '#34d399', background: 'rgba(52,211,153,0.1)',
              border: '1px solid rgba(52,211,153,0.25)', borderRadius: '4px', padding: '1px 6px'
            }}>
              <Sparkles size={10} /> AUTO-DETECTED
            </span>
          )}
          {activeProfile.description}
        </div>
      )}

      {loadError && (
        <div style={{ fontSize: '11px', color: '#f59e0b', marginTop: '10px', fontFamily: 'JetBrains Mono, monospace' }}>
          Couldn't reach the backend to load playbook profiles. Make sure the API server is running, then refresh.
        </div>
      )}

      <div style={{ marginTop: '14px' }}>
        <button
          onClick={() => setShowCustomForm(!showCustomForm)}
          style={{
            background: 'none', border: 'none', color: '#818cf8', cursor: 'pointer',
            fontSize: '12px', fontFamily: 'JetBrains Mono, monospace', padding: 0,
            display: 'flex', alignItems: 'center', gap: '6px'
          }}
        >
          <Plus size={13} /> {showCustomForm ? 'Hide custom rules' : `Add custom org rule${customRules.length ? ` (${customRules.length})` : ''}`}
        </button>

        {showCustomForm && (
          <div style={{ marginTop: '14px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {customRules.map((rule, idx) => (
              <div key={idx} style={{
                display: 'flex', alignItems: 'center', gap: '10px',
                background: 'rgba(255,255,255,0.03)', border: '1px solid var(--border-subtle)',
                borderRadius: '6px', padding: '8px 12px'
              }}>
                <div style={{ flex: 1, fontSize: '12px', color: 'var(--text-heading)' }}>
                  {rule.title} <span style={{ color: 'var(--text-faint)' }}>— flags: {rule.bad_patterns}</span>
                </div>
                <button onClick={() => removeCustomRule(idx)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-muted)' }}>
                  <X size={14} />
                </button>
              </div>
            ))}

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
              <input
                placeholder="Rule title (e.g. No MD5 password hashing)"
                value={draftTitle}
                onChange={(e) => setDraftTitle(e.target.value)}
                style={{ background: 'var(--bg-input)', border: '1px solid var(--border-subtle)', borderRadius: '6px', padding: '8px 10px', color: 'var(--text-heading)', fontSize: '12px' }}
              />
              <input
                placeholder="Forbidden patterns, comma separated (e.g. md5(, sha1()"
                value={draftPatterns}
                onChange={(e) => setDraftPatterns(e.target.value)}
                style={{ background: 'var(--bg-input)', border: '1px solid var(--border-subtle)', borderRadius: '6px', padding: '8px 10px', color: 'var(--text-heading)', fontSize: '12px' }}
              />
            </div>
            <input
              placeholder="Fix hint (optional)"
              value={draftFix}
              onChange={(e) => setDraftFix(e.target.value)}
              style={{ background: 'var(--bg-input)', border: '1px solid var(--border-subtle)', borderRadius: '6px', padding: '8px 10px', color: 'var(--text-heading)', fontSize: '12px' }}
            />
            <button
              onClick={addCustomRule}
              disabled={!draftTitle.trim() || !draftPatterns.trim()}
              style={{
                alignSelf: 'flex-start', padding: '7px 14px', borderRadius: '6px',
                background: 'rgba(129,140,248,0.12)', border: '1px solid rgba(129,140,248,0.3)',
                color: '#c7d2fe', fontSize: '12px', cursor: 'pointer'
              }}
            >
              Add rule
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
