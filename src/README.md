# Source Code Plan

Implementation has not started. The planned modular Python package is:

```text
src/
├── app.py                 # Streamlit review interface and input selection
├── video_io.py            # frame decoding and timestamp alignment
├── scene_config.py        # crossing polygon and camera settings
├── detection.py           # selected pretrained detector wrapper
├── tracking.py            # within-clip track association
├── interactions.py        # pair windows and motion/visibility features
├── conflict_rules.py      # transparent candidate scoring baseline
├── train.py               # linear SVM and training-only hard-negative mining
├── evaluate.py            # run-separated event metrics and plots
└── explain.py             # evidence fields and linear-model contributions
```

Keep model inference, scoring, interface, and evaluation logic separate. Record configurations and random seeds. Do not commit raw data or downloaded detector weights.
