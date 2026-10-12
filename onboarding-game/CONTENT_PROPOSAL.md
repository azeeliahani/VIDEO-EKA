# EKA Onboarding Quest: proposed content

A 90-day new joiner game presented by EKA. There are **3 stages (one per month)** with **5 tasks each**.
A stage unlocks only when **all 5 tasks in the previous month are done** and **that month has started** (30 and 60 days after the start date).

The game is `onboarding-game/index.html`. All the content below lives in the `CONTENT` object at the top of its `<script>`, so HR can edit questions without touching the game code.

| Rule | Detail |
|---|---|
| Tasks per month | 5 (mix of digital mini games and real-world missions) |
| Unlock | All 5 tasks done **and** month start date reached |
| Rewards | XP per task (1,980 XP total), a badge per month, a certificate after Month 3 |
| Pass marks | Quizzes and sorting games have a pass mark. Failing gives a "Try again" with EKA's tips |
| Preview mode | Settings toggle that skips the calendar wait (for HR, managers and demos) |
| Progress | Saved in the browser (localStorage) per person |

---

## Month 1 · Settle In (badge: Explorer)

*Goal: find your way around people, tools, values and staying safe.*

| # | Task | Game type | Content | Pass |
|---|---|---|---|---|
| 1 | Welcome Quiz | Multiple choice | Buddy vs manager, where policies live, first goals, IT tickets, how to ask EKA | 4 / 5 |
| 2 | Tool Match | Memory card flip | Teams, Outlook, SharePoint, HR Portal, IT Service Desk, EKA (Copilot), each paired with what it's for | All pairs |
| 3 | Values in Action | Sort into 2 bins | 8 behaviours: "Living our values" vs "Off track" (password sharing, owning mistakes, inclusion, data handling) | 7 / 8 |
| 4 | Phishing Spotter | Spot the difference | Fake "IT Support" email with 4 red flags: spoofed domain, urgency, password request, disguised link | Find all 4 |
| 5 | First-Week Mission | Real-world checklist | Laptop and badge, MFA set-up, buddy coffee, 30-day goals with manager, mandatory e-learning | All 5 ticked |

## Month 2 · Connect (badge: Connector)

*Goal: learn who does what, speak the language and work well with EKA.*

| # | Task | Game type | Content | Pass |
|---|---|---|---|---|
| 1 | Department Dash | Timed quiz (15 s) | Route 5 situations to the right team: Payroll, IT, Legal/Procurement, Corporate Comms, IT Security | 4 / 5 |
| 2 | Jargon Jumble | Word scramble | STAKEHOLDER, GOVERNANCE, METADATA, MILESTONE, ESCALATE, each with a clue | Finish all 5 (1 skip) |
| 3 | Build the Knowledge Hub | Sequence puzzle | EKA's 8 building blocks in order: Understand, Content, Metadata, Format, Governance, Automation, Copilot Agent, Analytics | Correct order |
| 4 | Prompt Like a Pro | Pick the better prompt | 4 pairs of weak vs strong Copilot prompts (context, format, tone, checking sources) | 3 / 4 |
| 5 | Network Builder | Real-world checklist | 3 coffee chats outside the team, join a community, half-day shadowing, a town hall, 60-day check-in | All 5 ticked |

## Month 3 · Contribute (badge: Contributor)

*Goal: put it all together by protecting data, serving customers and setting goals.*

| # | Task | Game type | Content | Pass |
|---|---|---|---|---|
| 1 | True or False Blitz | Rapid fire (10 s) | 8 data privacy and security statements (screen lock, personal cloud, public AI tools, badges, clear desk) | 6 / 8 |
| 2 | The Upset Customer | Branching scenario | 3-step customer conversation: empathy first, check history, escalate with an owner and a date | Reach the best outcome |
| 3 | SMART Goal Sorter | Sort into 2 bins | 6 goals: SMART vs too vague | 5 / 6 |
| 4 | Incident Response Run | Sequence puzzle | Suspected hacked account: stop, disconnect if advised, report, record, follow IT | Correct order |
| 5 | 90-Day Reflection | Reflect and commit | One win, one improvement idea for new joiners, next-quarter goal, plus confirming the probation review is booked | All 3 answered |

When all 15 tasks are done, the map shows a **certificate of completion** to bring to the probation review.

---

## Customising for your organisation

- **Values:** replace the Values in Action behaviours with your organisation's own values.
- **Tools:** swap the Tool Match pairs for your real stack (for example Workday, ServiceNow or Viva Engage).
- **Teams:** update Department Dash to match your organisation chart and escalation paths.
- **Policies:** check the True or False Blitz answers against your current Data Privacy and Information Security policies.
- **Timing:** change `DAYS_PER_STAGE` (default 30) if your stages aren't calendar months.
- **Preview mode:** it is on by default so the whole game can be reviewed. Turn it off in Settings (or set `preview: false` in the default state) for live rollout so the calendar gate applies.

## Ideas for a later version

- Manager sign-off on the real-world checklists, with progress stored centrally instead of in the browser.
- Leaderboard per intake cohort.
- EKA voice lines reusing the existing voice-over pipeline (`scripts/add_voiceover.sh`).
- Embed the EKA explainer video (`output/v2/`) as a Month 2 "watch and answer" task.
