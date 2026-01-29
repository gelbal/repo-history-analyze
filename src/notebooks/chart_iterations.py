# ABOUTME: Marimo notebook demonstrating AI-assisted chart design improvements.
# ABOUTME: Shows iterative progression from Plotly defaults to polished visualizations.

import marimo

__generated_with = "0.18.4"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _(mo):
    mo.md("""
    # From Default to Delightful: AI-Assisted Chart Design

    This notebook demonstrates how AI helps create effective visualizations
    through iterative improvements. We start with Plotly defaults and
    progressively apply dataviz best practices.

    **Data**: WordPress commit history (2005-2026)

    **Metrics**: Unique authors + Lines added/deleted (12-week rolling windows)
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
    DATA_DIR = PROJECT_ROOT / "data"
    return DATA_DIR, go, make_subplots, pd


@app.cell
def _(DATA_DIR, pd):
    # Load the rolling window aggregates data
    df = pd.read_csv(DATA_DIR / "WordPress" / "rolling_window_aggregates.csv")
    df["window_start"] = pd.to_datetime(df["window_start"])
    df
    return (df,)


@app.cell
def _(mo):
    mo.md("""
    ## Iteration 1: Plotly Defaults

    **AI Prompt**: "Create line charts showing unique authors and lines changed over time"

    This is what Plotly gives us out of the box. No customization at all.
    """)
    return


@app.cell
def _(df, go, make_subplots):
    # Iteration 1: Pure Plotly defaults - side by side charts
    fig1 = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Unique Authors", "Lines Changed")
    )

    # Authors chart
    fig1.add_trace(
        go.Scatter(x=df["window_start"], y=df["unique_authors"], mode="lines", name="Authors"),
        row=1, col=1
    )

    # Lines added/deleted chart
    fig1.add_trace(
        go.Scatter(x=df["window_start"], y=df["total_lines_added"], mode="lines", name="Added"),
        row=1, col=2
    )
    fig1.add_trace(
        go.Scatter(x=df["window_start"], y=df["total_lines_deleted"], mode="lines", name="Deleted"),
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
    white, reduce gridline prominence, format the x-axis dates to show just years, format
    y-axis numbers with K/M suffixes, and add clear axis labels."

    **Principles applied**: Remove chart junk, improve readability, align time axes
    """)
    return


@app.cell
def _(df, go, make_subplots):
    # Iteration 2: Decluttered with aligned time axes (stacked vertically)
    fig2 = make_subplots(
        rows=2, cols=1,
        subplot_titles=("Unique Authors", "Lines Changed"),
        vertical_spacing=0.12
    )

    # Authors chart
    fig2.add_trace(
        go.Scatter(x=df["window_start"], y=df["unique_authors"], mode="lines", name="Authors"),
        row=1, col=1
    )

    # Lines added/deleted chart
    fig2.add_trace(
        go.Scatter(
            x=df["window_start"], y=df["total_lines_added"],
            mode="lines", name="Added"
        ),
        row=2, col=1
    )
    fig2.add_trace(
        go.Scatter(
            x=df["window_start"], y=df["total_lines_deleted"],
            mode="lines", name="Deleted"
        ),
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

    # Y-axis labels and formatting
    fig2.update_yaxes(title_text="Authors", row=1, col=1)
    fig2.update_yaxes(title_text="Lines Changed", tickformat=".2s", row=2, col=1)

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
    - K/M suffixes make large numbers readable

    **Next**: Apply meaningful colors that tell a story
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## Iteration 3: Brand Colors, No Gridlines, Peak Annotations

    **AI Prompt**: "Apply WordPress brand colors and remove gridlines completely for a
    cleaner look. Add inline annotations showing the peak number of authors at key
    5-year intervals (around 2010, 2012, 2015, 2017, and 2024) so the viewer can see
    the growth trajectory without needing to trace to the y-axis."

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
        subplot_titles=("Unique Authors", "Lines Changed"),
        vertical_spacing=0.12
    )

    # Authors chart - WordPress blue
    fig3.add_trace(
        go.Scatter(
            x=df["window_start"], y=df["unique_authors"],
            mode="lines", name="Authors",
            line=dict(color=WP_BLUEBERRY, width=2.5)
        ),
        row=1, col=1
    )

    # Lines added - green (growth)
    fig3.add_trace(
        go.Scatter(
            x=df["window_start"], y=df["total_lines_added"],
            mode="lines", name="Added",
            line=dict(color=WP_ACID_GREEN, width=2.5)
        ),
        row=2, col=1
    )

    # Lines deleted - red (removal)
    fig3.add_trace(
        go.Scatter(
            x=df["window_start"], y=df["total_lines_deleted"],
            mode="lines", name="Deleted",
            line=dict(color=WP_POMEGRADE, width=2.5)
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

    fig3.update_yaxes(title_text="Authors", row=1, col=1)
    fig3.update_yaxes(title_text="Lines Changed", tickformat=".2s", row=2, col=1)

    # Peak annotations for authors chart at ~5-year intervals
    _author_peaks = [
        ("2009-12-28", 11),   # Around 2010
        ("2012-07-09", 22),   # Local max 2010-2015
        ("2015-11-02", 31),   # Just after 2015
        ("2017-08-07", 29),   # Between 2015-2020
        ("2024-09-02", 38),   # Just before 2025
    ]
    for _date_str, _authors in _author_peaks:
        fig3.add_annotation(
            x=_date_str, y=_authors,
            text=str(_authors),
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
    - Semantic colors: green=added (growth), red=deleted (removal)
    - **Gridlines removed** - cleaner, less cluttered appearance
    - **Peak annotations** show growth trajectory (11 → 22 → 31 → 29 → 38 authors)
    - Reader can see exact values without tracing to y-axis

    **Next**: Remove axis labels entirely and annotate at data peaks
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## Iteration 4: No Axis Labels, Annotations at Data Peaks

    **AI Prompt**: "Remove y-axis labels completely - let the data speak for itself.
    Instead of labeling line endpoints, annotate at the most significant peak point.
    Place '922K lines added' and '668K deleted' annotations at the Gutenberg-era spike
    (September 2018) where code churn was highest."

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
            "Unique Authors per 12-Week Window",
            "Lines Changed per 12-Week Window"
        ),
        vertical_spacing=0.15
    )

    # Authors chart
    fig4.add_trace(
        go.Scatter(
            x=df["window_start"], y=df["unique_authors"],
            mode="lines", line=dict(color=WP_BLUEBERRY_4, width=2),
            showlegend=False
        ),
        row=1, col=1
    )

    # Lines added
    fig4.add_trace(
        go.Scatter(
            x=df["window_start"], y=df["total_lines_added"],
            mode="lines", line=dict(color=WP_ACID_GREEN_4, width=2),
            showlegend=False
        ),
        row=2, col=1
    )

    # Lines deleted
    fig4.add_trace(
        go.Scatter(
            x=df["window_start"], y=df["total_lines_deleted"],
            mode="lines", line=dict(color=WP_POMEGRADE_4, width=2),
            showlegend=False
        ),
        row=2, col=1
    )

    # Find max lines added peak (Gutenberg era, Sept 2018)
    max_idx = df["total_lines_added"].idxmax()
    max_row = df.loc[max_idx]
    peak_date = max_row["window_start"]
    peak_added = max_row["total_lines_added"]
    peak_deleted = max_row["total_lines_deleted"]

    # Annotations at peak for lines added/deleted
    fig4.add_annotation(
        x=peak_date, y=peak_added,
        text=f"{peak_added/1000:.0f}K lines added",
        showarrow=True, arrowhead=0,
        ax=50, ay=-25,
        font=dict(color=WP_ACID_GREEN_4, size=11),
        row=2, col=1
    )
    fig4.add_annotation(
        x=peak_date, y=peak_deleted,
        text=f"{peak_deleted/1000:.0f}K deleted",
        showarrow=True, arrowhead=0,
        ax=50, ay=25,
        font=dict(color=WP_POMEGRADE_4, size=11),
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
            text="WordPress Development Activity",
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

    # No y-axis labels - annotations speak for themselves
    fig4.update_yaxes(tickformat=".2s", row=2, col=1)

    # Peak annotations for authors chart at ~5-year intervals
    _author_peaks_4 = [
        ("2009-12-28", 11),
        ("2012-07-09", 22),
        ("2015-11-02", 31),
        ("2017-08-07", 29),
        ("2024-09-02", 38),
    ]
    for _date_str, _authors in _author_peaks_4:
        fig4.add_annotation(
            x=_date_str, y=_authors,
            text=str(_authors),
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
    - Annotations placed at the **data peak** (Sept 2018 Gutenberg spike) not endpoints
    - Reader immediately sees the most dramatic moment in the data
    - Descriptive subplot titles explain what each chart shows
    - Overall title with date range frames the data set

    **Next**: Transform from data display into data story
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## Iteration 5: Storytelling - Complete Narrative

    **AI Prompt**: "Transform this from a data display into a data story. Add a takeaway
    title that states the key insight. Annotate notable WordPress milestones like major
    releases or the Gutenberg launch. Frame the narrative around the project's evolution."

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
            "Unique Authors per 12-Week Window",
            "Lines Changed per 12-Week Window"
        ),
        vertical_spacing=0.15
    )

    # Authors chart
    fig5.add_trace(
        go.Scatter(
            x=df["window_start"], y=df["unique_authors"],
            mode="lines", line=dict(color=WP_BLUEBERRY_5, width=2),
            showlegend=False
        ),
        row=1, col=1
    )

    # Lines added
    fig5.add_trace(
        go.Scatter(
            x=df["window_start"], y=df["total_lines_added"],
            mode="lines", line=dict(color=WP_ACID_GREEN_5, width=2),
            showlegend=False
        ),
        row=2, col=1
    )

    # Lines deleted
    fig5.add_trace(
        go.Scatter(
            x=df["window_start"], y=df["total_lines_deleted"],
            mode="lines", line=dict(color=WP_POMEGRADE_5, width=2),
            showlegend=False
        ),
        row=2, col=1
    )

    # Find max lines added peak (Gutenberg era, Sept 2018)
    max_idx_5 = df["total_lines_added"].idxmax()
    max_row_5 = df.loc[max_idx_5]
    peak_date_5 = max_row_5["window_start"]
    peak_added_5 = max_row_5["total_lines_added"]
    peak_deleted_5 = max_row_5["total_lines_deleted"]

    # Annotations at peak for lines added/deleted
    fig5.add_annotation(
        x=peak_date_5, y=peak_added_5,
        text=f"{peak_added_5/1000:.0f}K lines added",
        showarrow=True, arrowhead=0,
        ax=50, ay=-25,
        font=dict(color=WP_ACID_GREEN_5, size=11),
        row=2, col=1
    )
    fig5.add_annotation(
        x=peak_date_5, y=peak_deleted_5,
        text=f"{peak_deleted_5/1000:.0f}K deleted",
        showarrow=True, arrowhead=0,
        ax=50, ay=25,
        font=dict(color=WP_POMEGRADE_5, size=11),
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
        # Vertical line on BOTTOM chart (row 2) - no text
        fig5.add_vline(
            x=_date_str, line=dict(color=WP_CHARCOAL_5, width=1, dash="dot"),
            row=2, col=1
        )
        # Annotation only on row 1
        _y_max = df["unique_authors"].max()
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
                "WordPress: Two Decades of Open Source Growth<br>"
                "<sup>Contributor community expanded 10x while maintaining healthy code churn</sup>"
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

    # No y-axis labels - annotations speak for themselves
    fig5.update_yaxes(tickformat=".2s", row=2, col=1)

    # Peak annotations for authors chart at ~5-year intervals
    _author_peaks_5 = [
        ("2009-12-28", 11),
        ("2012-07-09", 22),
        ("2015-11-02", 31),
        ("2017-08-07", 29),
        ("2024-09-02", 38),
    ]
    for _date_str, _authors in _author_peaks_5:
        fig5.add_annotation(
            x=_date_str, y=_authors,
            text=str(_authors),
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
    | Colors | Random defaults | Brand palette with semantic meaning |
    | Legend | External box | Inline labels |
    | Context | None | Date range + milestone annotations |
    | Layout | Side-by-side | Vertically aligned for comparison |
    | Message | "Here's data" | "Here's what the data means" |

    **Key insight**: The same data tells a completely different story when presented well.
    AI assistants can apply these dataviz principles systematically, making professional-quality
    charts accessible to everyone.
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
def _(fig1, fig2, fig3, fig4, fig5):
    import os
    from pathlib import Path as ExportPath

    # Collect all figures with their output filenames
    all_charts = {
        "fig1": (fig1, "iteration_1_defaults.png"),
        "fig2": (fig2, "iteration_2_decluttered.png"),
        "fig3": (fig3, "iteration_3_brand_colors.png"),
        "fig4": (fig4, "iteration_4_embedded_labels.png"),
        "fig5": (fig5, "iteration_5_storytelling.png"),
    }

    def export_charts(charts=all_charts):
        """Export all chart figures to PNG files in the plots/ directory."""
        # Create plots directory relative to notebook location
        notebook_dir = ExportPath(__file__).parent.resolve()
        plots_path = notebook_dir / "plots"
        os.makedirs(plots_path, exist_ok=True)

        exported_files = []
        for fig_key, (figure, filename) in charts.items():
            output_path = plots_path / filename
            figure.write_image(str(output_path), scale=2, width=1200, height=800)
            exported_files.append(str(output_path))

        return exported_files

    # Uncomment the line below to export charts:
    export_charts()
    return


if __name__ == "__main__":
    app.run()
