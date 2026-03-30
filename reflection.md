# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

Four classes: Task holds a single activity's data (title, duration, frequency, status). Pet owns a list of Tasks and handles adding/retrieving them. Owner manages one or more Pets and provides a flat view of all tasks. Scheduler is the logic layer — it queries, sorts, and manages tasks without touching the data classes directly.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

Yes. Task originally had no `time_of_day` field — sorting was only by frequency and duration. Added `time_of_day` (morning/afternoon/evening/anytime) to make the schedule actually reflect a real day. Also changed `mark_task_complete()` from returning a `bool` to a `(bool, str)` tuple so the caller can tell whether the task was renewed or just finished.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

Time of day is the primary sort key, frequency is secondary (daily before weekly), duration is the tiebreak (longer first). Time of day came first because a schedule without "when" is just a list.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

Conflict detection uses a 90-minute threshold per slot rather than exact start-time collision detection. Since tasks have slots (morning/afternoon) not precise times, an exact overlap check is not meaningful — total load per slot is a reasonable proxy for "too much crammed in."

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

Used AI to draft class stubs, plan method signatures, and generate test boilerplate. The most useful prompts were specific and outcome-focused: "what should this method return so the caller can distinguish renewal from completion" produced a cleaner interface than asking open-ended design questions.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

An early suggestion included a `priority` field (high/medium/low) on Task. Rejected it because frequency already signals urgency for this use case and adding a separate priority enum added complexity without a concrete payoff. Verified by asking: "what would I actually do with this field in the scheduler?" — no good answer, so it was cut.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

Task completion status, pet task count after addition, scheduler filtering out completed tasks, chronological sort order, recurring task renewal, non-recurring task non-renewal, conflict detection for overloaded slots and duplicate titles. Each test targets a distinct behavior that could silently break if the logic changed.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

High confidence for the behaviors covered. Would test next: two pets with the same task title (does conflict detection fire incorrectly?), renewing a task that was already renewed multiple times, and a schedule with all tasks in the "anytime" slot.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

Keeping Pet and Owner as clean data classes with no logic in them. All the intelligence sits in Scheduler, which made each piece straightforward to test in isolation.

**b. What you would improve**

- If you had another iteration, what would you redesign?

Recurring tasks currently spawn a new copy immediately on completion rather than scheduling it for the next day. Real date tracking would make recurrence meaningful instead of just growing the task list indefinitely.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

Separating data from logic early (data classes vs. a logic class) is the single decision that made everything else easier — testing, extending, and debugging each became straightforward because nothing was tangled together.
