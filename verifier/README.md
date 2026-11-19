# verifier

Deterministic check between a drafted report and the observed events.
A claim reaches the therapist only if the cited events exist and support it.

Evidence levels: 1 movement, 2 prescribed exercise performed, 3 activity done
independently (needs patient report or therapist observation), 4 functional
progress (therapist only, never generated).

Rules: cited events must exist; level cannot exceed what the sources support
(sensors 2, patient report 3); numbers must match the events; missing data is
"not observed", never "did not do"; a session where sensor and report disagree
must be flagged; progress is never written by the system.

    python3 run_eval.py                 # verifier vs hand-labeled drafts (3 synthetic scenarios)
    python3 run_ollama.py llama3.2:3b   # drafts from a local model, then verified

The hand-labeled result is circular (same author for rules and drafts). The meaningful
measurement uses model-written drafts labeled by a therapist.
