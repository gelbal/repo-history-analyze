# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo",
#     "plotly>=5.0",
#     "pandas>=2.0",
#     "kaleido",
# ]
# ///
# ABOUTME: Marimo notebook demonstrating AI-assisted chart design improvements.
# ABOUTME: Shows iterative progression visualizing WordPress Props contributors over time.

import marimo

__generated_with = "0.19.6"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _(mo):
    mo.md("""
    # From Default to Delightful: WordPress Props Contributors

    This notebook demonstrates how AI helps create effective visualizations
    through iterative improvements. We start with Plotly defaults and
    progressively apply dataviz best practices.

    **Data**: WordPress SVN commit history (2003-2026)

    **Metric**: Unique Props contributors per 12-week rolling window

    Props is WordPress's attribution system that credits everyone who contributed
    to a change - not just the committer, but also reviewers, testers, bug
    reporters, and patch authors.
    """)
    return


@app.cell
def _():
    from pathlib import Path
    import pandas as pd
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    # Compute paths relative to this notebook's location
    NOTEBOOK_DIR = Path(__file__).parent.resolve()
    PROJECT_ROOT = NOTEBOOK_DIR.parent.parent  # src/notebooks -> src -> project root
    DATA_DIR = PROJECT_ROOT / "data" / "svn" / "marimo"
    return DATA_DIR, NOTEBOOK_DIR, PROJECT_ROOT, go, make_subplots, pd


@app.cell
def _(DATA_DIR, pd):
    # Load the rolling window aggregates data
    df = pd.read_csv(DATA_DIR / "rolling_12week_stats.csv")
    df["date"] = pd.to_datetime(df["date"])
    df
    return (df,)


@app.cell
def _(mo):
    mo.md("""
    ## Iteration 1: Plotly Defaults

    **AI Prompt**: "Create line charts showing unique Props contributors and committers over time"

    This is what Plotly gives us out of the box. No customization at all.
    """)
    return


@app.cell
def _(df, go, make_subplots):
    # Iteration 1: Pure Plotly defaults - side by side charts
    fig1 = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Props Contributors", "Committers")
    )

    # Props contributors chart
    fig1.add_trace(
        go.Scatter(x=df["date"], y=df["unique_props_contributors"], mode="lines", name="Props"),
        row=1, col=1
    )

    # Committers chart
    fig1.add_trace(
        go.Scatter(x=df["date"], y=df["unique_authors"], mode="lines", name="Committers"),
        row=1, col=2
    )

    fig1.update_layout(height=400)
    fig1
    return (fig1,)


@app.cell
def _(mo):
    mo.md("""
    ### What's wrong with the defaults?

    - No descriptive title
    - Generic axis labels (just column names)
    - Cluttered background with dark gridlines
    - Default colors don't tell a story
    - Hard to read date format on x-axis
    - Legend placement takes up space
    - No context about what the data means

    Let's improve this step by step...
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## Iteration 2: Declutter and Structure

    **AI Prompt**: "Clean up these charts by removing visual clutter. Make the background
    white, reduce gridline prominence, format the x-axis dates to show just years,
    and add clear axis labels. Stack the charts vertically to align time axes."

    **Principles applied**: Remove chart junk, improve readability, align time axes
    """)
    return


@app.cell
def _(df, go, make_subplots):
    # Iteration 2: Decluttered with aligned time axes (stacked vertically)
    fig2 = make_subplots(
        rows=2, cols=1,
        subplot_titles=("Props Contributors", "Committers"),
        vertical_spacing=0.12
    )

    # Props contributors chart
    fig2.add_trace(
        go.Scatter(x=df["date"], y=df["unique_props_contributors"], mode="lines", name="Props"),
        row=1, col=1
    )

    # Committers chart
    fig2.add_trace(
        go.Scatter(x=df["date"], y=df["unique_authors"], mode="lines", name="Committers"),
        row=2, col=1
    )

    # Clean up layout
    fig2.update_layout(
        height=600,
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(size=12),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    # Format axes for both subplots
    fig2.update_xaxes(
        tickformat="%Y",
        showgrid=True,
        gridcolor="#e0e0e0",
        zeroline=False
    )
    fig2.update_yaxes(
        showgrid=True,
        gridcolor="#e0e0e0",
        zeroline=False
    )

    # Y-axis labels
    fig2.update_yaxes(title_text="Contributors", row=1, col=1)
    fig2.update_yaxes(title_text="Committers", row=2, col=1)

    fig2
    return (fig2,)


@app.cell
def _(mo):
    mo.md("""
    ### What improved?

    - White background removes visual noise
    - Subtle gridlines guide the eye without distraction
    - Vertical stacking aligns time axes for easy comparison
    - Year-only date format is cleaner

    **Next**: Apply meaningful colors that tell a story
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## Iteration 3: Brand Colors, No Gridlines, Peak Annotations

    **AI Prompt**: "Apply WordPress brand colors and remove gridlines completely for a
    cleaner look. Add inline annotations showing the peak number of Props contributors
    at key intervals so the viewer can see the growth trajectory without needing to
    trace to the y-axis."

    **Principles applied**: Brand consistency, semantic colors, minimal chrome, inline data labels
    """)
    return


@app.cell
def _(df, go, make_subplots):
    # WordPress brand colors
    WP_BLUEBERRY = "#3858e9"
    WP_ACID_GREEN = "#33f078"
    WP_POMEGRADE = "#e26f56"
    WP_CHARCOAL = "#1e1e1e"

    # Iteration 3: Brand colors with semantic meaning
    fig3 = make_subplots(
        rows=2, cols=1,
        subplot_titles=("Props Contributors", "Committers"),
        vertical_spacing=0.12
    )

    # Props contributors chart - WordPress blue
    fig3.add_trace(
        go.Scatter(
            x=df["date"], y=df["unique_props_contributors"],
            mode="lines", name="Props",
            line=dict(color=WP_BLUEBERRY, width=2.5)
        ),
        row=1, col=1
    )

    # Committers chart - WordPress green
    fig3.add_trace(
        go.Scatter(
            x=df["date"], y=df["unique_authors"],
            mode="lines", name="Committers",
            line=dict(color=WP_ACID_GREEN, width=2.5)
        ),
        row=2, col=1
    )

    # Layout with brand colors
    fig3.update_layout(
        height=600,
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(size=12, color=WP_CHARCOAL),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    # Styled axes - no gridlines for cleaner look
    fig3.update_xaxes(
        tickformat="%Y",
        showgrid=False,
        zeroline=False,
        tickfont=dict(color=WP_CHARCOAL)
    )
    fig3.update_yaxes(
        showgrid=False,
        zeroline=False,
        tickfont=dict(color=WP_CHARCOAL)
    )

    fig3.update_yaxes(title_text="Contributors", row=1, col=1)
    fig3.update_yaxes(title_text="Committers", row=2, col=1)

    # Peak annotations for Props contributors chart at key intervals
    _props_peaks = [
        ("2010-01-04", 110),
        ("2013-01-07", 191),
        ("2016-01-04", 227),
        ("2018-10-22", 617),
        ("2022-01-03", 262),
    ]
    for _date_str, _props in _props_peaks:
        fig3.add_annotation(
            x=_date_str, y=_props,
            text=str(_props),
            showarrow=False,
            yshift=12,
            font=dict(color=WP_BLUEBERRY, size=10, weight="bold"),
            row=1, col=1
        )

    fig3
    return (fig3,)


@app.cell
def _(mo):
    mo.md("""
    ### What improved?

    - WordPress brand colors create visual identity
    - **Gridlines removed** - cleaner, less cluttered appearance
    - **Peak annotations** show growth trajectory (110 → 191 → 227 → 617 → 262 contributors)
    - Reader can see exact values without tracing to y-axis
    - The Gutenberg peak (617) stands out dramatically

    **Next**: Remove axis labels entirely and annotate at data peaks
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## Iteration 4: No Axis Labels, Annotations at Data Peaks

    **AI Prompt**: "Remove y-axis labels completely - let the data speak for itself.
    Show the community multiplier by annotating the ratio of Props contributors
    to committers at the peak activity period (Gutenberg launch)."

    **Principles applied**: Minimal axis chrome, direct labeling at peaks, meaningful titles
    """)
    return


@app.cell
def _(df, go, make_subplots):
    # WordPress brand colors
    WP_BLUEBERRY_4 = "#3858e9"
    WP_ACID_GREEN_4 = "#33f078"
    WP_POMEGRADE_4 = "#e26f56"
    WP_CHARCOAL_4 = "#1e1e1e"

    # Iteration 4: Embedded legends and meaningful titles
    fig4 = make_subplots(
        rows=2, cols=1,
        subplot_titles=(
            "Unique Props Contributors per 12-Week Window",
            "Unique Committers per 12-Week Window"
        ),
        vertical_spacing=0.15
    )

    # Props contributors chart
    fig4.add_trace(
        go.Scatter(
            x=df["date"], y=df["unique_props_contributors"],
            mode="lines", line=dict(color=WP_BLUEBERRY_4, width=2),
            showlegend=False
        ),
        row=1, col=1
    )

    # Committers chart
    fig4.add_trace(
        go.Scatter(
            x=df["date"], y=df["unique_authors"],
            mode="lines", line=dict(color=WP_ACID_GREEN_4, width=2),
            showlegend=False
        ),
        row=2, col=1
    )

    # Find peak Props contributors (Gutenberg era, Oct 2018)
    max_idx_4 = df["unique_props_contributors"].idxmax()
    max_row_4 = df.loc[max_idx_4]
    peak_date_4 = max_row_4["date"]
    peak_props_4 = max_row_4["unique_props_contributors"]
    peak_committers_4 = max_row_4["unique_authors"]

    # Annotation at peak for Props contributors
    fig4.add_annotation(
        x=peak_date_4, y=peak_props_4,
        text=f"{int(peak_props_4)} Props contributors",
        showarrow=True, arrowhead=0,
        ax=60, ay=-25,
        font=dict(color=WP_BLUEBERRY_4, size=11),
        row=1, col=1
    )

    # Annotation showing ratio at peak
    _ratio = peak_props_4 / peak_committers_4 if peak_committers_4 > 0 else 0
    fig4.add_annotation(
        x=peak_date_4, y=peak_committers_4,
        text=f"{int(peak_committers_4)} committers ({_ratio:.0f}x multiplier)",
        showarrow=True, arrowhead=0,
        ax=80, ay=25,
        font=dict(color=WP_ACID_GREEN_4, size=11),
        row=2, col=1
    )

    # Layout
    fig4.update_layout(
        height=600,
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(size=12, color=WP_CHARCOAL_4),
        showlegend=False,
        title=dict(
            text="WordPress Props: The Community Behind the Code",
            x=0.5, xanchor="center",
            font=dict(size=16, color=WP_CHARCOAL_4)
        ),
        margin=dict(r=80)
    )

    # Axes styling - no gridlines for cleaner look
    fig4.update_xaxes(
        tickformat="%Y",
        showgrid=False,
        zeroline=False, tickfont=dict(color=WP_CHARCOAL_4)
    )
    fig4.update_yaxes(
        showgrid=False,
        zeroline=False, tickfont=dict(color=WP_CHARCOAL_4)
    )

    # Peak annotations for Props chart at key intervals
    _props_peaks_4 = [
        ("2010-01-04", 110),
        ("2013-01-07", 191),
        ("2016-01-04", 227),
        ("2022-01-03", 262),
    ]
    for _date_str, _props in _props_peaks_4:
        fig4.add_annotation(
            x=_date_str, y=_props,
            text=str(_props),
            showarrow=False,
            yshift=12,
            font=dict(color=WP_BLUEBERRY_4, size=10, weight="bold"),
            row=1, col=1
        )

    fig4
    return (fig4,)


@app.cell
def _(mo):
    mo.md("""
    ### What improved?

    - **Y-axis labels removed** - the annotations provide context
    - Annotations placed at the **data peak** (Oct 2018 Gutenberg launch)
    - Reader immediately sees the most dramatic moment in the data
    - Community multiplier shown: for each committer, many more Props contributors
    - Descriptive subplot titles explain what each chart shows

    **Next**: Transform from data display into data story
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## Iteration 5: Storytelling - Complete Narrative

    **AI Prompt**: "Transform this from a data display into a data story. Add a takeaway
    title that states the key insight. Annotate notable WordPress milestones like major
    releases or the Gutenberg launch. Frame the narrative around how Props captures
    the full breadth of community involvement."

    **Principles applied**: Insight-driven titles, contextual annotations, narrative framing
    """)
    return


@app.cell
def _(df, go, make_subplots):
    # WordPress brand colors
    WP_BLUEBERRY_5 = "#3858e9"
    WP_ACID_GREEN_5 = "#33f078"
    WP_POMEGRADE_5 = "#e26f56"
    WP_CHARCOAL_5 = "#1e1e1e"

    # Iteration 5: Full storytelling with milestones
    fig5 = make_subplots(
        rows=2, cols=1,
        subplot_titles=(
            "Unique Props Contributors per 12-Week Window",
            "Unique Committers per 12-Week Window"
        ),
        vertical_spacing=0.15
    )

    # Props contributors chart
    fig5.add_trace(
        go.Scatter(
            x=df["date"], y=df["unique_props_contributors"],
            mode="lines", line=dict(color=WP_BLUEBERRY_5, width=2),
            showlegend=False
        ),
        row=1, col=1
    )

    # Committers chart
    fig5.add_trace(
        go.Scatter(
            x=df["date"], y=df["unique_authors"],
            mode="lines", line=dict(color=WP_ACID_GREEN_5, width=2),
            showlegend=False
        ),
        row=2, col=1
    )

    # Find peak Props contributors (Gutenberg era)
    max_idx_5 = df["unique_props_contributors"].idxmax()
    max_row_5 = df.loc[max_idx_5]
    peak_date_5 = max_row_5["date"]
    peak_props_5 = max_row_5["unique_props_contributors"]
    peak_committers_5 = max_row_5["unique_authors"]

    # Annotation at peak for Props contributors
    fig5.add_annotation(
        x=peak_date_5, y=peak_props_5,
        text=f"{int(peak_props_5)} Props contributors",
        showarrow=True, arrowhead=0,
        ax=60, ay=-25,
        font=dict(color=WP_BLUEBERRY_5, size=11),
        row=1, col=1
    )

    # Annotation showing ratio at peak
    _ratio_5 = peak_props_5 / peak_committers_5 if peak_committers_5 > 0 else 0
    fig5.add_annotation(
        x=peak_date_5, y=peak_committers_5,
        text=f"{int(peak_committers_5)} committers ({_ratio_5:.0f}x multiplier)",
        showarrow=True, arrowhead=0,
        ax=80, ay=25,
        font=dict(color=WP_ACID_GREEN_5, size=11),
        row=2, col=1
    )

    # Key WordPress milestones with vertical lines and annotations
    _milestones = [
        ("2010-06-17", "WP 3.0\nMultisite"),
        ("2018-12-06", "Gutenberg\n(WP 5.0)"),
        ("2022-05-24", "WP 6.0\nFull Site Editing"),
    ]

    for _date_str, _label in _milestones:
        # Vertical line on TOP chart (row 1)
        fig5.add_vline(
            x=_date_str, line=dict(color=WP_CHARCOAL_5, width=1, dash="dot"),
            row=1, col=1
        )
        # Vertical line on BOTTOM chart (row 2)
        fig5.add_vline(
            x=_date_str, line=dict(color=WP_CHARCOAL_5, width=1, dash="dot"),
            row=2, col=1
        )
        # Annotation only on row 1
        _y_max = df["unique_props_contributors"].max()
        fig5.add_annotation(
            x=_date_str, y=_y_max * 0.95,
            text=_label,
            showarrow=False,
            font=dict(size=9, color=WP_CHARCOAL_5),
            bgcolor="rgba(255,255,255,0.8)",
            row=1, col=1
        )

    # Layout with insight-driven title
    fig5.update_layout(
        height=650,
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(size=12, color=WP_CHARCOAL_5),
        showlegend=False,
        title=dict(
            text=(
                "WordPress Props: Recognizing the Full Community<br>"
                "<sup>For every committer, 20+ contributors are credited via Props</sup>"
            ),
            x=0.5, xanchor="center",
            font=dict(size=16, color=WP_CHARCOAL_5)
        ),
        margin=dict(r=80, t=80)
    )

    # Axes styling - no gridlines for cleaner look
    fig5.update_xaxes(
        tickformat="%Y",
        showgrid=False,
        zeroline=False, tickfont=dict(color=WP_CHARCOAL_5)
    )
    fig5.update_yaxes(
        showgrid=False,
        zeroline=False, tickfont=dict(color=WP_CHARCOAL_5)
    )

    # Peak annotations for Props chart at key intervals
    _props_peaks_5 = [
        ("2010-01-04", 110),
        ("2013-01-07", 191),
        ("2016-01-04", 227),
        ("2022-01-03", 262),
    ]
    for _date_str, _props in _props_peaks_5:
        fig5.add_annotation(
            x=_date_str, y=_props,
            text=str(_props),
            showarrow=False,
            yshift=12,
            font=dict(color=WP_BLUEBERRY_5, size=10, weight="bold"),
            row=1, col=1
        )

    fig5
    return (fig5,)


@app.cell
def _(mo):
    mo.md("""
    ### The Complete Transformation

    Compare Iteration 1 (Plotly defaults) with Iteration 5 (storytelling):

    | Aspect | Before | After |
    |--------|--------|-------|
    | Title | Generic subplot labels | Insight-driven headline |
    | Colors | Random defaults | WordPress brand palette |
    | Legend | External box | Inline labels at peaks |
    | Context | None | Milestone annotations |
    | Layout | Side-by-side | Vertically aligned for comparison |
    | Message | "Here's data" | "Props captures the full community" |

    **Key insight**: WordPress's Props system credits 20x more contributors than
    just committers alone. The same data tells a completely different story when
    presented with context and purpose.
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## Export Charts as PNG

    Export all chart iterations to PNG files for use in presentations or documentation.
    """)
    return


@app.cell
def _(NOTEBOOK_DIR, fig1, fig2, fig3, fig4, fig5):
    import os

    # Collect all figures with their output filenames
    all_charts = {
        "fig1": (fig1, "props_iteration_1_defaults.png"),
        "fig2": (fig2, "props_iteration_2_decluttered.png"),
        "fig3": (fig3, "props_iteration_3_brand_colors.png"),
        "fig4": (fig4, "props_iteration_4_embedded_labels.png"),
        "fig5": (fig5, "props_iteration_5_storytelling.png"),
    }

    def export_charts(charts=all_charts):
        """Export all chart figures to PNG files in the plots/ directory."""
        plots_path = NOTEBOOK_DIR / "plots"
        os.makedirs(plots_path, exist_ok=True)

        exported_files = []
        for fig_key, (figure, filename) in charts.items():
            output_path = plots_path / filename
            figure.write_image(str(output_path), scale=2, width=1200, height=800)
            exported_files.append(str(output_path))

        return exported_files

    # Uncomment the line below to export charts:
    # export_charts()
    return


if __name__ == "__main__":
    app.run()
