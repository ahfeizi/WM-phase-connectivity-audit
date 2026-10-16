# Screening manual

Title-and-abstract screening rules for the phase-connectivity reporting audit.
Applies to `stage0_output/screening_sheet.csv`.

This document has two jobs. It is the instruction set for the LLM pre-screening
pass, and it is the source text for the screening subsection of the methods. Any
change to it after screening begins is a protocol deviation and is logged.

---

## Roles

**Pre-screening pass (LLM).** Fills `ai_label` and `ai_reason` for every record.
Advisory only. No record is included or excluded on this basis.

**Human screener (author).** Fills `include` and `exclusion_reason` for every
record, having read the title and abstract. This is the authoritative decision.
Every `ai_label` is reviewed, not only the ones that look wrong.

Agreement between `ai_label` and `include` is computed afterwards and reported.
It is a descriptive statistic about the pre-screening tool, not a validity claim.

---

## Decision

Read the title and abstract. Assign one of three labels.

### `1` — include

All four must hold:

1. **Empirical, human.** Original data collected from human participants.
2. **Scalp EEG.** EEG recorded from the scalp is the modality on which
   connectivity is computed.
3. **Inter-regional phase-based connectivity.** At least one connectivity
   measure derived from phase relationships **between two or more
   electrodes/sources** is reported. Examples: PLV, coherence, phase coherence,
   PLI, wPLI, dwPLI, imaginary coherency, ciPLV, phase synchronization index.
4. **Working-memory task.** Connectivity is computed during, or contrasted
   across conditions of, a task with an explicit working-memory load or
   retention demand.

### `0` — exclude

Any one of the exclusion criteria below applies. Record the reason code.

### `?` — cannot decide from the abstract

Use `?` **only** when the connectivity measure is unspecified and every other
eligibility condition is satisfied. The abstract says "functional connectivity",
"network", "coupling" or "synchronization" without naming the index, and the
study is otherwise clearly an empirical scalp-EEG study with a working-memory
task.

If any other condition is plainly violated — no working-memory task, a study
protocol rather than results, resting-state only, no EEG — the label is `0`,
regardless of whether the abstract contains a connectivity word.

`?` means "the abstract cannot settle eligibility". It does not mean "I want to
look at this again later".

---

## Exclusion reason codes

Use exactly these strings.

| Code | Applies when |
|------|--------------|
| `review` | Review, systematic review, meta-analysis, commentary, editorial, letter, protocol, conference abstract, book chapter, erratum |
| `no-EEG` | MEG-only, fMRI-only, fNIRS-only, intracranial/ECoG-only, or animal study. A study reporting EEG alongside another modality is **not** excluded |
| `no-WM` | No working-memory task, or the cognitive demand is something else (attention, inhibition, language, motor, emotion, resting cognition) |
| `resting-only` | Connectivity computed only at rest or only pre/post task, with no task-based connectivity contrast |
| `no-phase-connectivity` | No inter-regional phase-based measure: power/amplitude only, amplitude-envelope correlation, within-channel phase-amplitude coupling only, Granger/directed measures without a phase measure, graph metrics on a non-phase adjacency matrix, inter-brain or brain-behaviour synchrony |
| `simulation` | Simulation, modelling, or methods-development paper with no empirical working-memory application |
| `small-N` | Fewer than 10 participants in the analysed sample |
| `clinical-only` | Single-case or clinical study where no working-memory connectivity contrast is reported |
| `classification-only` | A phase-based measure is computed solely as an input feature to a classifier or predictive model, with no statistical inference reported about the connectivity itself |

If more than one applies, record the first that applies in the order listed.

---

## Hard cases, decided in advance

These are the recurring judgment calls. Decide them this way every time.

**Attention, updating, inhibition, executive control.** Exclude as `no-WM`
unless the task itself imposes a retention or load manipulation. An n-back is
working memory; a flanker task is not; a Stroop task is not; a sustained-attention
task is not. Being described as "executive function" is not sufficient.

**Short-term memory and visual short-term memory.** Include. Change-detection
and delayed match-to-sample paradigms count, as does a delay-period contrast in a
visual array task.

**Inter-brain synchrony / hyperscanning.** Exclude as `no-phase-connectivity`.
The measure is between people, not between regions within a brain, and the
volume-conduction question does not arise in the same form.

**Phase-amplitude coupling.** Exclude as `no-phase-connectivity` if PAC is the
only coupling measure and it is computed within a channel. If PAC is computed
between two distinct sites **and** a within-frequency inter-regional phase measure
is also reported, include.

**Stimulus- or response-locked phase locking.** "Phase locking" is frequently
used to mean inter-trial phase consistency at a single electrode (ITPC/ITC).
That is not connectivity. Exclude as `no-phase-connectivity` unless an
inter-electrode measure is also reported.

**Graph-theory papers.** Include only if the adjacency matrix is built from a
phase-based measure. If the abstract says "graph metrics" without naming the
connectivity measure, label `?`.

**"Coherence" in a non-signal sense.** Speech coherence, therapeutic coherence,
cardiac coherence, optical coherence tomography. Exclude as
`no-phase-connectivity`.

**tACS/tDCS/TMS studies.** Include if scalp-EEG phase connectivity during a
working-memory task is reported. Stimulation is not itself an exclusion.

**Clinical populations.** Include. Patient samples are eligible; the audit is
about reporting practice, not about healthy participants.

**Children and older adults.** Include. No age restriction.

**Multiple papers on the same dataset.** Include each separately at this stage
and flag the overlap during coding. Do not deduplicate by dataset here.

**Machine-learning classification studies.** Exclude as `classification-only`
when a phase-based measure enters a classifier as a feature and no inferential
claim about connectivity is made. The audit is about how researchers reason
from phase-synchrony estimates to conclusions about coupling; a classifier that
consumes PLV as a feature makes no such claim, and the volume-conduction problem
takes a different form there. If the paper reports both a classification
analysis **and** a statistical contrast on the connectivity measure, include it.

---

## `ai_reason` format

One short clause, lowercase, no trailing period. State the fact that drove the
decision, not the rule that was applied.

Good: `n-back with wPLI between frontal and parietal sites`
Good: `inter-trial phase coherence at single electrodes only`
Good: `abstract says functional connectivity, measure not specified`

Bad: `meets criteria 1-4`
Bad: `this appears to be a relevant study about working memory and connectivity`

---

## Output

The pre-screening pass writes back to the same CSV, filling `ai_label` and
`ai_reason` only. No other column is touched, no row is reordered, and no row is
removed. `rec_id` is the stable key.
