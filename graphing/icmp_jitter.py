#!/usr/bin/env python3
"""
Graphing definitions for ICMP Extension to Active Check (Jitter and MOS)
"""

from cmk.graphing.v1 import graphs, metrics, perfometers, Title

# Metric definitions for jitter
# Use DecimalNotation with "s" suffix to match existing RTA metrics
metric_jitter_avg = metrics.Metric(
    name="jitter_avg",
    title=Title("Average jitter"),
    unit=metrics.Unit(metrics.DecimalNotation("s")),
    color=metrics.Color.BLUE,
)

metric_jitter_max = metrics.Metric(
    name="jitter_max",
    title=Title("Maximum jitter"),
    unit=metrics.Unit(metrics.DecimalNotation("s")),
    color=metrics.Color.PURPLE,
)

metric_jitter_min = metrics.Metric(
    name="jitter_min",
    title=Title("Minimum jitter"),
    unit=metrics.Unit(metrics.DecimalNotation("s")),
    color=metrics.Color.CYAN,
)

metric_mos = metrics.Metric(
    name="mos",
    title=Title("Mean Opinion Score (MOS)"),
    unit=metrics.Unit(metrics.DecimalNotation("")),
    color=metrics.Color.GREEN,
)

# Graph for jitter metrics only
graph_jitter = graphs.Graph(
    name="jitter",
    title=Title("Network jitter"),
    simple_lines=[
        "jitter_avg",
        "jitter_max",
        "jitter_min",
    ],
    optional=[
        "jitter_max",
        "jitter_min",
    ],
)

# Graph for MOS score
graph_mos = graphs.Graph(
    name="mos_score",
    title=Title("Voice quality (MOS)"),
    simple_lines=[
        "mos",
    ],
)

# Perfometer for jitter
perfometer_jitter = perfometers.Perfometer(
    name="jitter",
    focus_range=perfometers.FocusRange(
        perfometers.Closed(0),
        perfometers.Closed(0.1),  # 100ms in seconds
    ),
    segments=["jitter_avg"],
)

# Perfometer for MOS
perfometer_mos = perfometers.Perfometer(
    name="mos",
    focus_range=perfometers.FocusRange(
        perfometers.Closed(1.0),
        perfometers.Closed(4.4),
    ),
    segments=["mos"],
)
