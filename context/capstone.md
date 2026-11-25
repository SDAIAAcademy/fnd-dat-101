---
course: "SQL and Relational Data"
code: "FND-DAT-101"
version: "2027.1.0"
deck: "capstone"
day: 5
language: "en"
view: "trainee"
source: "https://sdaiaacademy.github.io/fnd-dat-101/slides/capstone.html"
---

# SQL and Relational Data

## Capstone: Capstone: the business orders brief

For each participant: five minutes of live adaptation of one query, then two of questions on the assumptions note

#### [capstone#title] Capstone: the business orders brief

*SDAIA Academy · SQL and Relational Data*

Capstone: For each participant: five minutes of live adaptation of one query, then two of questions on the assumptions note

Data & AI Foundations Track · 4 teaching days + capstone day · 5 min talk and demo · 2 min Q&A · FND-DAT-101

#### [capstone#agenda] How the day runs

*Capstone day*

- **Opening**: the rubric and the format
- **Timed check**: assistant off, on paper
- **Final preparation**: finish the repository, run the tests, push
- **Live adaptations**: one query each, then questions on the assumptions note
- **Reviews and next steps**: peer review, the trainer's review, the follow-up task

#### [capstone#rubric] The rubric

*How the repository is scored · 30% of the course*

| Item | Value |
| --- | --- |
| Correct: the ten queries match the key on the full data | 35% |
| Tests against a fixture checked by hand, and they pass | 20% |
| Grain stated for every query and join | 15% |
| Assumptions note: every rule stated, applied and traced | 15% |
| Verification log of generated SQL | 10% |
| Minimal exposure: no personal data a question does not need | 5% |

#### [capstone#format] Five minutes to adapt one query live, then two minutes of questions

*Format*

- **1 · The change.** The trainer reads a changed version of one of your ten questions.
- **2 · The query.** You change it, add a fixture row if needed, and run its test.
- **3 · The reason.** You say what changed in the grain or the rules.

> **Then two minutes on your assumptions note.** Expect "where is this rule applied?" and "why did you decide this?"

#### [capstone#timed-check] Ten questions · 40 minutes

*Timed check · assistant off*

Two printed tables, ten short questions. Predict, explain, write one query on paper.

#### [capstone#final-prep] Final preparation · 120 minutes

*Before the first adaptation*

Run `uv run pytest capstone/tests -q`, fill in the notes, commit and push.

#### [capstone#running-order] Who adapts when

*Running order*

| # | Participant | Query to adapt | # | Participant | Query to adapt |
| --- | --- | --- | --- | --- | --- |
| 1 |  |  | 9 |  |  |
| 2 |  |  | 10 |  |  |
| 3 |  |  | 11 |  |  |
| 4 |  |  | 12 |  |  |
| 5 |  |  | 13 |  |  |
| 6 |  |  | 14 |  |  |
| 7 |  |  | 15 |  |  |
| 8 |  |  | 16 |  |  |

#### [capstone#now-presenting] Now adapting

*Now adapting*

#### [capstone#peer-review] Run a classmate's tests and read one of their queries against the rules

*Peer review · 50 minutes*

- Clone the repository of the participant after you in the running order
- Run its tests; pick one query and check its grain comment against the query
- Write one strength, one question and one suggestion as an issue on their repository

#### [capstone#review] What the repositories showed

*Trainer review*

- **Strongest patterns.** What several repositories got right.
- **Common gaps.** The traps most answers fell into.
- **One surprise.** Something nobody expected.

#### [capstone#follow-up] Two new questions from the business orders service, answered the same way

*Follow-up task · within two weeks*

- The trainer sends two questions after the course; you add `q11.sql` and `q12.sql` to your repository
- Each with its grain comment, its expected rows worked by hand and a passing test
- About an hour; the commits on your repository are the record that it was done

#### [capstone#what-next] Keep going

*After the course*

- **Your repository stays yours:** keep its tests running when you change a query
- **Next Academy course:** FND-DAT-102 Data Wrangling with DataFrames, then FND-DAT-103 Data Formats, Interfaces and Quality Checks

#### [capstone#thanks] Thank you

*SDAIA Academy*

SQL and Relational Data
