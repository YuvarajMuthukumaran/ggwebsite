"""The one booking block, used wherever a visitor can ask to be called back.

Every page ends with the same panel: what a consultation costs and when it runs, both
consulting rooms, the callback form, and the two ways to reach the team now. Built here
so it is written once (the review asked for one component, not a variant per template).

The form posts to /api/callback. With JavaScript it stays on the page and swaps in the
thank-you panel; without it, the browser posts the form and lands on /thank-you/.

Facts come from data/site.json through the placeholder dict, and a row whose fact is
still waiting on a decision is left out rather than rendered empty.
"""

WHO = [('self', 'Myself'), ('family', 'A family member')]
CLINICS = [('delhi', 'New Delhi'), ('gurugram', 'Gurugram'), ('online', 'Online')]

ICON = {
    'phone': '<path d="M6.5 3h3l1.5 4-2 1.5a12 12 0 0 0 5.5 5.5L16 12l4 1.5v3a2 2 0 0 1-2.2 2A16.5 16.5 0 0 1 4 6.2 2 2 0 0 1 6.5 3z"/>',
    'clock': '<circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/>',
    'pin': '<path d="M12 21s-7-5.6-7-11a7 7 0 0 1 14 0c0 5.4-7 11-7 11z"/><circle cx="12" cy="10" r="2.5"/>',
    'rupee': '<path d="M7 4h10M7 8.5h10M16 4c0 4-3 4.5-6 4.5h-.5L16 20"/>',
}


def esc(s):
    return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')


def ico(name):
    return ('<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.6" '
            'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">%s</svg>' % ICON[name])


def facts_rows(v):
    """Fee, timings and the rooms. A fact still waiting on a decision is simply not shown."""
    rows = []
    fee, mins = v.get('fee', ''), v.get('session', '')
    if fee:
        rows.append(('rupee', 'Consultation', esc(fee) + (' for %s minutes' % esc(mins) if mins else '')))
    times = [(label, v.get(key, '')) for label, key in
             (('New Delhi', 'opd_delhi'), ('Gurugram', 'opd_gurugram'), ('Online', 'opd_online'))]
    times = [(l, t) for l, t in times if t]
    if times:
        rows.append(('clock', 'OPD', '; '.join('%s %s' % (esc(l), esc(t)) for l, t in times)))
    for label, key in (('New Delhi', 'addr_delhi'), ('Gurugram', 'addr_gurugram')):
        if v.get(key):
            rows.append(('pin', label, esc(v[key])))
    rows.append(('phone', 'Call', esc(v.get('phone', ''))))
    return ('<ul class="bp-facts">%s</ul>'
            % ''.join('<li><span class="bp-facts__ic">%s</span><span><b>%s</b><small>%s</small></span></li>'
                      % (ico(i), k, val) for i, k, val in rows))


def field(name, label, required, kind='text', hint='', **attrs):
    extra = ''.join(' %s="%s"' % (k.replace('_', '-'), esc(x)) for k, x in attrs.items())
    req = ' required aria-required="true"' if required else ''
    opt = '' if required else ' <span class="bp-opt">(optional)</span>'
    hint_html = '<p class="bp-hint" id="bp-%s-h">%s</p>' % (name, hint) if hint else ''
    described = ' aria-describedby="bp-%s-h"' % name if hint else ''
    tag = ('<textarea id="bp-%s" name="%s" rows="3" maxlength="600"%s%s%s></textarea>' % (name, name, req, described, extra)
           if kind == 'textarea' else
           '<input id="bp-%s" name="%s" type="%s"%s%s%s>' % (name, name, kind, req, described, extra))
    return ('<p class="bp-field"><label for="bp-%s">%s%s</label>%s%s'
            '<span class="bp-err" id="bp-%s-e" hidden></span></p>' % (name, label, opt, tag, hint_html, name))


def choice(name, legend, options, default=None):
    opts = ''.join(
        '<label class="bp-choice"><input type="radio" name="%s" value="%s"%s><span>%s</span></label>'
        % (name, val, ' checked' if val == default else '', esc(label)) for val, label in options)
    return ('<fieldset class="bp-set"><legend>%s</legend><div class="bp-choices" data-choice="%s">%s</div>'
            '<span class="bp-err" id="bp-%s-e" hidden></span></fieldset>' % (legend, name, opts, name))


def form(root, page_path):
    # Each field sits in its own "step" div. Without JS this is invisible -- every step shows
    # at once and the form works exactly as it always did, one page, one submit. assets/js/
    # bp-wizard.js is what turns it into a one-question-at-a-time flow; see that file's own
    # comment for how the two stay in sync (required-ness, server-side errors, the lot).
    steps = [
        ('name', field('name', 'Your name', True, autocomplete='name', maxlength='80')),
        ('phone', field('phone', 'Mobile number', True, kind='tel', autocomplete='tel',
                        hint='A 10-digit Indian mobile, so the team can call you back.')),
        ('who', choice('who', 'Who is the consultation for?', WHO, 'self')),
        ('clinic', choice('clinic', 'Where would you like to be seen?', CLINICS)),
        ('concern', field('concern', 'What would you like help with?', False, kind='textarea',
                          hint='A sentence is enough. You do not have to be sure what is wrong.')
                    + '<button class="btn bp-submit" type="submit">Request a call back</button>'
                      '<p class="bp-note">We call back during OPD hours. Nothing is shared outside the clinic team.</p>'),
    ]
    steps_html = ''.join('<div class="bp-step" data-step="%s">%s</div>' % (name, html) for name, html in steps)
    return ('<form class="bp-form" id="bp-form" method="post" action="/api/callback/" novalidate>'
            '<input type="hidden" name="page" value="/%s">'
            '<p class="bp-pot" aria-hidden="true"><label for="bp-website">Leave this empty</label>'
            '<input id="bp-website" name="website" type="text" tabindex="-1" autocomplete="off"></p>'
            '<input type="hidden" name="utm_source"><input type="hidden" name="utm_medium"><input type="hidden" name="utm_campaign">'
            '%s'
            '</form>'
            % (page_path, steps_html))


def thanks(v):
    """The panel swapped in after a successful send (also the body of /thank-you/)."""
    return ('<div class="bp-thanks" id="bp-thanks" hidden><span class="bp-thanks__tick" aria-hidden="true">'
            '<svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" stroke-width="2" '
            'stroke-linecap="round" stroke-linejoin="round"><path d="m5 12.5 4.5 4.5L19 7.5"/></svg></span>'
            '<h3 tabindex="-1">Thank you, the team has your request.</h3>'
            '<p>Someone from Dr. Gupta&rsquo;s team will call you back%s to find a time that suits you. '
            'The call comes from a Delhi number.</p>'
            '<p class="bp-thanks__now">If it is urgent, call <a href="%s">%s</a> now.</p></div>'
            % ((' ' + esc(v['callback_hours'])) if v.get('callback_hours') else ' during OPD hours',
               esc(v.get('phone_href', '')), esc(v.get('phone', ''))))


def panel(root, v, page_path, heading='Ask for a call back'):
    lede = ('Leave your number and the team calls you back. For a consultation in New Delhi or Gurugram, '
            'or online, for yourself or for someone in your family.')
    return ('<section class="bp" id="book" aria-labelledby="bp-h">'
            '<div class="bp__in"><div class="bp__l"><p class="bp-k">Book a consultation</p>'
            '<h2 id="bp-h">%s</h2><p class="bp-lede">%s</p>%s'
            '<div class="bp-now"><a class="btn ghost" href="%s">%s Call %s</a>'
            '<a class="btn ghost" href="%s" target="_blank" rel="noopener">WhatsApp</a></div></div>'
            '<div class="bp__r">%s%s</div></div></section>'
            % (esc(heading), lede, facts_rows(v), esc(v.get('phone_href', '')), ico('phone'), esc(v.get('phone', '')),
               esc(v.get('wa', '')), form(root, page_path), thanks(v)))
