# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo",
#     "plotly>=5.0",
#     "pandas>=2.0",
#     "kaleido",
# ]
# ///
# ABOUTME: Marimo notebook visualizing WordPress SVN development activity over time.
# ABOUTME: Shows iterative chart improvements combining contributors and line changes.

import marimo

__generated_with = "0.19.7"
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
    progressively apply data visualization best practices.

    **Data**: WordPress SVN commit history (2003-2025)

    **Metrics**: Contributors + Lines added/deleted (quarterly rolling windows)

    WordPress tracks contributors via the `Props` tag in commit messages — crediting
    not just committers, but also reviewers, testers, bug reporters, and patch authors.
    In this notebook, we use "Contributors" to refer to all individuals credited via `Props`.

    WordPress has grown from a simple blogging tool to the world's most popular
    CMS, powering over 40% of all websites.
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
    return DATA_DIR, NOTEBOOK_DIR, go, make_subplots, pd


@app.cell
def _(DATA_DIR, pd):
    # Load the rolling window aggregates data (for time series charts)
    df = pd.read_csv(DATA_DIR / "rolling_12week_stats.csv")
    df["date"] = pd.to_datetime(df["date"])
    # Calculate net lines
    df["net_lines"] = df["total_lines_added"] - df["total_lines_deleted"]

    # Load weekly stats for accurate totals (non-overlapping)
    df_weekly = pd.read_csv(DATA_DIR / "weekly_stats.csv")
    df_weekly["date"] = pd.to_datetime(df_weekly["date"])
    df_weekly["net_lines"] = df_weekly["total_lines_added"] - df_weekly["total_lines_deleted"]

    df
    return df, df_weekly


@app.cell
def _(mo):
    mo.md("""
    ## Iteration 0: Raw Weekly Data

    The weekly charts show raw activity. This is useful for operational monitoring
    but too noisy for trend analysis.

    Weekly data is noisy. Single large commits, code imports, or
    vendor updates create dramatic spikes that obscure underlying trends. Seasonal patterns (holidays, release cycles) create gaps

    **The Solution**: A 12-week (quarterly) rolling window smooths this noise,
    revealing trends via sustained activity patterns rather than one-off events.
    """)
    return


@app.cell
def _(df_weekly, go, make_subplots):
    # Iteration 0: Raw weekly data with Plotly defaults
    fig0 = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Contributors (Weekly)", "Lines Changed (Weekly)")
    )

    # Contributors chart - weekly
    fig0.add_trace(
        go.Scatter(x=df_weekly["date"], y=df_weekly["unique_props_contributors"],
                   mode="lines", name="Contributors"),
        row=1, col=1
    )

    # Lines added/deleted - weekly
    fig0.add_trace(
        go.Scatter(x=df_weekly["date"], y=df_weekly["total_lines_added"],
                   mode="lines", name="Added"),
        row=1, col=2
    )
    fig0.add_trace(
        go.Scatter(x=df_weekly["date"], y=df_weekly["total_lines_deleted"],
                   mode="lines", name="Deleted"),
        row=1, col=2
    )

    fig0.update_layout(height=400)
    fig0
    return (fig0,)


@app.cell
def _(mo):
    mo.md("""
    ## Iteration 1: Plotly Defaults (Rolling Data)

    **AI Prompt**: "Create line charts showing contributors over time in one chart,
    and lines added and deleted in a second chart"

    Now using quarterly rolling aggregates. This is what Plotly gives us out of the box.
    """)
    return


@app.cell
def _(df, go, make_subplots):
    # Iteration 1: Pure Plotly defaults - side by side charts
    fig1 = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Contributors", "Lines Changed")
    )

    # Contributors chart
    fig1.add_trace(
        go.Scatter(x=df["date"], y=df["unique_props_contributors"], mode="lines", name="Contributors"),
        row=1, col=1
    )

    # Lines added/deleted chart
    fig1.add_trace(
        go.Scatter(x=df["date"], y=df["total_lines_added"], mode="lines", name="Added"),
        row=1, col=2
    )
    fig1.add_trace(
        go.Scatter(x=df["date"], y=df["total_lines_deleted"], mode="lines", name="Deleted"),
        row=1, col=2
    )

    fig1.update_layout(height=400)
    fig1
    return (fig1,)


@app.cell
def _(mo):
    mo.md("""
    ### What's wrong with the defaults?

    - No descriptive title.
    - Generic axis labels (just column names).
    - Cluttered background with dark gridlines.
    - Default colors don't tell a story.
    - Legend placement takes up space.
    - No context about what the data means.

    Let's improve this step by step...
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## Iteration 2: Declutter and Structure

    **AI Prompt**: "Clean up these charts by removing visual clutter. Make the background
    white, reduce gridline prominence. Draw the charts in 2 rows instead of 2 columns,
    so the x-axis is shared."

    **Principles applied**: Remove chart junk, improve readability, align time axes
    """)
    return


@app.cell
def _(df, go, make_subplots):
    # Semantic colors for Iteration 2
    COLOR_ADDED_2 = "#22c55e"   # Green - growth
    COLOR_DELETED_2 = "#ef4444"  # Red - removal

    # Iteration 2: Decluttered with aligned time axes (stacked vertically)
    fig2 = make_subplots(
        rows=2, cols=1,
        subplot_titles=("Contributors", "Lines Changed"),
        vertical_spacing=0.12,
        shared_xaxes=True
    )

    # Contributors chart
    fig2.add_trace(
        go.Scatter(x=df["date"], y=df["unique_props_contributors"], mode="lines", name="Contributors"),
        row=1, col=1
    )

    # Lines added/deleted chart - semantic colors
    fig2.add_trace(
        go.Scatter(
            x=df["date"], y=df["total_lines_added"],
            mode="lines", name="Added",
            line=dict(color=COLOR_ADDED_2, width=2)
        ),
        row=2, col=1
    )
    fig2.add_trace(
        go.Scatter(
            x=df["date"], y=df["total_lines_deleted"],
            mode="lines", name="Deleted",
            line=dict(color=COLOR_DELETED_2, width=2)
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
        showgrid=True,
        gridcolor="#e0e0e0",
        zeroline=False
    )
    fig2.update_yaxes(
        showgrid=True,
        gridcolor="#e0e0e0",
        zeroline=False
    )

    fig2
    return (fig2,)


@app.cell
def _(mo):
    mo.md("""
    ### What improved?

    - White background removes visual noise.
    - Subtle gridlines guide the eye without distraction.
    - Vertical stacking aligns time axes for easy comparison.
    - Shared x-axis makes temporal comparison intuitive.
    - Semantic colors: green for growth, red for removal.

    **Next**: We can do better by adopting WordPress brand colors and customization.
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## Iteration 3: WordPress Brand Colors, No Gridlines, Peak Annotations

    **AI Prompt**: "Apply official WordPress brand colors and remove gridlines completely
    for a cleaner look. Add inline annotations showing the peak number of contributors
    at key intervals so the viewer can see the growth trajectory without needing to
    trace to the y-axis."

    **Principles applied**: Brand consistency, minimal chrome, inline data labels
    """)
    return


@app.cell
def _(df, go, make_subplots):
    # Official WordPress Brand Colors
    WP_BLUE = "#21759b"        # WordPress Blue - Contributors
    WP_CERULEAN = "#00aadc"    # Cerulean - Lines Added
    WP_ORANGE = "#d54e21"      # WordPress Orange - Lines Deleted
    WP_DARK_GRAY = "#464646"   # Text color

    # Iteration 3: Brand colors with semantic meaning
    fig3 = make_subplots(
        rows=2, cols=1,
        subplot_titles=("Contributors", "Lines Changed"),
        vertical_spacing=0.12,
        shared_xaxes=True
    )

    # Contributors chart - WordPress blue
    fig3.add_trace(
        go.Scatter(
            x=df["date"], y=df["unique_props_contributors"],
            mode="lines", name="Contributors",
            line=dict(color=WP_BLUE, width=2.5)
        ),
        row=1, col=1
    )

    # Lines added - Cerulean
    fig3.add_trace(
        go.Scatter(
            x=df["date"], y=df["total_lines_added"],
            mode="lines", name="Added",
            line=dict(color=WP_CERULEAN, width=2.5)
        ),
        row=2, col=1
    )

    # Lines deleted - WordPress orange
    fig3.add_trace(
        go.Scatter(
            x=df["date"], y=df["total_lines_deleted"],
            mode="lines", name="Deleted",
            line=dict(color=WP_ORANGE, width=2.5)
        ),
        row=2, col=1
    )

    # Layout with brand colors and Open Sans font
    fig3.update_layout(
        height=600,
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="Open Sans, sans-serif", size=12, color=WP_DARK_GRAY),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    # Styled axes - no gridlines for cleaner look
    fig3.update_xaxes(
        tickformat="%Y",
        showgrid=False,
        zeroline=False,
        tickfont=dict(color=WP_DARK_GRAY)
    )
    fig3.update_yaxes(
        showgrid=False,
        zeroline=False,
        tickfont=dict(color=WP_DARK_GRAY)
    )

    # Use ~s format to avoid "0.0" display
    fig3.update_yaxes(tickformat="~s", row=2, col=1)

    # Peak annotations for contributors chart - with dates
    # (date, value, yshift, xshift, label)
    _contributor_peaks = [
        ("2007-01-01", 10, 18, 0, "10\n(Jan 2007)"),
        ("2010-04-05", 307, 18, 0, "307\n(Apr 2010)"),
        ("2013-09-16", 479, 18, 0, "479\n(Sep 2013)"),
        ("2018-10-22", 631, 18, 0, "631\n(Oct 2018)"),
    ]
    for _date_str, _contributors, _yshift, _xshift, _label in _contributor_peaks:
        fig3.add_annotation(
            x=_date_str, y=_contributors,
            text=_label,
            showarrow=False,
            yshift=_yshift,
            xshift=_xshift,
            font=dict(color=WP_BLUE, size=11, weight="bold"),
            row=1, col=1
        )

    # Peak annotations for lines added chart - key milestones
    # (date, value, yshift, xshift, label)
    _lines_peaks = [
        ("2005-04-11", 201588, 18, 0, "202K\n(Apr 2005)"),     # WP 1.5
        ("2018-10-01", 171420, 18, 0, "171K\n(Oct 2018)"),   # WP 5.0 prep
        ("2021-01-18", 221648, 18, -20, "222K\n(Jan 2021)"),   # Peak activity
    ]
    for _date_str, _lines, _yshift, _xshift, _label in _lines_peaks:
        fig3.add_annotation(
            x=_date_str, y=_lines,
            text=_label,
            showarrow=False,
            yshift=_yshift,
            xshift=_xshift,
            font=dict(color=WP_CERULEAN, size=11, weight="bold"),
            row=2, col=1
        )

    fig3
    return (fig3,)


@app.cell
def _(mo):
    mo.md("""
    ### What improved?

    - WordPress brand colors and typography create visual identity.
    - Gridlines removed: cleaner, less cluttered appearance.
    - Peak annotations with dates show growth trajectory.
    - Reader can see exact values and when they occurred.

    **Next**: Add net code growth panel and make it even easier to read the chart.
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## Iteration 4: Add Net Growth Panel with Area Fills

    **AI Prompt**: "Add net code growth as a third panel. Use area fills to show
    magnitude more clearly. Add inline labels to all charts. Remove the legend.
    Left-align titles."

    **Principles applied**: Layered visualization, area fills for magnitude, inline labels
    """)
    return


@app.cell
def _(df, go, make_subplots):
    # Official WordPress Brand Colors
    WP_BLUE_4 = "#21759b"        # WordPress Blue - Contributors
    WP_CERULEAN_4 = "#00aadc"    # Cerulean - Lines Added
    WP_ORANGE_4 = "#d54e21"      # WordPress Orange - Lines Deleted
    WP_ORIENT_4 = "#005082"      # Orient Blue - Net Change
    WP_DARK_GRAY_4 = "#464646"   # Text color

    # Iteration 4: Three panels with area fills, no chart titles
    fig4 = make_subplots(
        rows=3, cols=1,
        vertical_spacing=0.08,
        shared_xaxes=True,
        row_heights=[0.33, 0.33, 0.34]
    )

    # Contributors chart with inline label
    fig4.add_trace(
        go.Scatter(
            x=df["date"], y=df["unique_props_contributors"],
            mode="lines", name="Contributors",
            line=dict(color=WP_BLUE_4, width=2),
            showlegend=False
        ),
        row=1, col=1
    )

    # Lines added - area fill
    fig4.add_trace(
        go.Scatter(
            x=df["date"], y=df["total_lines_added"],
            mode="lines", name="Added",
            line=dict(color=WP_CERULEAN_4, width=1.5),
            fill="tozeroy",
            fillcolor="rgba(0, 170, 220, 0.3)",
            showlegend=False
        ),
        row=2, col=1
    )

    # Lines deleted - area fill
    fig4.add_trace(
        go.Scatter(
            x=df["date"], y=df["total_lines_deleted"],
            mode="lines", name="Deleted",
            line=dict(color=WP_ORANGE_4, width=1.5),
            fill="tozeroy",
            fillcolor="rgba(213, 78, 33, 0.3)",
            showlegend=False
        ),
        row=2, col=1
    )

    # Net change - area fill
    fig4.add_trace(
        go.Scatter(
            x=df["date"], y=df["net_lines"],
            mode="lines", name="Net",
            line=dict(color=WP_ORIENT_4, width=2),
            fill="tozeroy",
            fillcolor="rgba(0, 80, 130, 0.3)",
            showlegend=False
        ),
        row=3, col=1
    )

    # Add zero line for net change
    fig4.add_hline(y=0, line=dict(color="#999", width=1, dash="dash"), row=3, col=1)

    # Inline label for Contributors (at end of line)
    _last_contrib = df.iloc[-1]
    fig4.add_annotation(
        x=_last_contrib["date"], y=_last_contrib["unique_props_contributors"],
        text="Contributors",
        showarrow=False,
        xshift=60,
        font=dict(color=WP_BLUE_4, size=18, weight="bold"),
        row=1, col=1
    )

    # Inline labels for Lines chart - spread vertically to avoid overlap
    _last_row = df.iloc[-1]
    fig4.add_annotation(
        x=_last_row["date"], y=_last_row["total_lines_added"],
        text="Lines Added",
        showarrow=False,
        xshift=55,
        yshift=25,  # Move up
        font=dict(color=WP_CERULEAN_4, size=18, weight="bold"),
        row=2, col=1
    )
    fig4.add_annotation(
        x=_last_row["date"], y=_last_row["total_lines_deleted"],
        text="Lines Deleted",
        showarrow=False,
        xshift=65,
        yshift=-20,  # Move down
        font=dict(color=WP_ORANGE_4, size=18, weight="bold"),
        row=2, col=1
    )

    # Inline label for Net change
    fig4.add_annotation(
        x=_last_row["date"], y=_last_row["net_lines"],
        text="Net",
        showarrow=False,
        xshift=30,
        font=dict(color=WP_ORIENT_4, size=18, weight="bold"),
        row=3, col=1
    )

    # Layout - left aligned title, no legend
    fig4.update_layout(
        height=750,
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="Open Sans, sans-serif", size=15, color=WP_DARK_GRAY_4),
        showlegend=False,
        title=dict(
            text="WordPress Development Activity (Quarterly)",
            x=0, xanchor="left",
            font=dict(size=26, color=WP_DARK_GRAY_4)
        ),
        margin=dict(r=120, l=60)
    )

    # Axes styling - use ~s to avoid "0.0"
    fig4.update_xaxes(
        tickformat="%Y",
        showgrid=False,
        zeroline=False,
        tickfont=dict(color=WP_DARK_GRAY_4, size=15)
    )
    fig4.update_yaxes(
        showgrid=False,
        zeroline=False,
        tickfont=dict(color=WP_DARK_GRAY_4, size=15),
        tickformat="~s"
    )

    # Peak annotations for contributors - with dates
    # (date, value, yshift, xshift, label)
    _contributor_peaks_4 = [
        ("2007-01-01", 10, 20, 0, "10\n(Jan 2007)"),
        ("2010-04-05", 307, 20, 0, "307\n(Apr 2010)"),
        ("2013-09-16", 479, 20, 0, "479\n(Sep 2013)"),
        ("2018-10-22", 631, 20, 0, "631\n(Oct 2018)"),
    ]
    for _date_str, _contributors, _yshift, _xshift, _label in _contributor_peaks_4:
        fig4.add_annotation(
            x=_date_str, y=_contributors,
            text=_label,
            showarrow=False,
            yshift=_yshift,
            xshift=_xshift,
            font=dict(color=WP_BLUE_4, size=17, weight="bold"),
            row=1, col=1
        )

    # Peak annotations for Lines Added - key milestones only
    # (date, value, yshift, xshift)
    _lines_added_peaks_4 = [
        ("2005-04-11", 201588, 20, 0),    # WP 1.5 release
        ("2020-11-30", 227664, 24, -4),   # Peak activity
    ]
    for _date_str, _lines, _yshift, _xshift in _lines_added_peaks_4:
        fig4.add_annotation(
            x=_date_str, y=_lines,
            text=f"{_lines/1000:.0f}K",
            showarrow=False,
            yshift=_yshift,
            xshift=_xshift,
            font=dict(color=WP_CERULEAN_4, size=17, weight="bold"),
            row=2, col=1
        )

    # Peak annotations for Lines Deleted - key milestone only
    # (date, value, yshift, xshift)
    _lines_deleted_peaks_4 = [
        ("2021-01-18", 204728, 18, 4),    # Peak deletions
    ]
    for _date_str, _lines, _yshift, _xshift in _lines_deleted_peaks_4:
        fig4.add_annotation(
            x=_date_str, y=_lines,
            text=f"{_lines/1000:.0f}K",
            showarrow=False,
            yshift=_yshift,
            xshift=_xshift,
            font=dict(color=WP_ORANGE_4, size=17, weight="bold"),
            row=2, col=1
        )

    # Peak annotations for Net Change - key peaks and valleys
    # (date, value, yshift, xshift)
    _net_peaks_4 = [
        ("2005-04-18", 196637, 20, 0),     # WP 1.5 release
        ("2017-12-18", -38622, -28, 0),    # Post WP 4.9 cleanup
        ("2018-10-08", 117674, 20, 0),     # WP 5.0 Gutenberg push
        ("2020-09-28", 112182, 20, 0),   # WP 5.5/5.6 development
        ("2021-02-15", -18864, -24, 0),     # Post 5.7 refactoring
        ("2023-08-07", 101879, 20, 0),   # WP 6.3 FSE maturity
        ("2024-10-07", -16242, -20, 0),     # WP 6.7 cleanup
    ]
    for _date_str, _net, _yshift, _xshift in _net_peaks_4:
        fig4.add_annotation(
            x=_date_str, y=_net,
            text=f"{_net/1000:+.0f}K" if _net >= 0 else f"{_net/1000:.0f}K",
            showarrow=False,
            yshift=_yshift,
            xshift=_xshift,
            font=dict(color=WP_ORIENT_4, size=17, weight="bold"),
            row=3, col=1
        )

    fig4
    return (fig4,)


@app.cell
def _(mo):
    mo.md("""
    ### What improved?

    - Three-panel layout shows contributors, lines of code changes, and net code growth. Reader immediately sees the three dimensions of activity.
    - Area fills show magnitude more clearly than lines alone.
    - Net growth panel reveals when WordPress grew vs churned code
    - Inline labels replace the legend to have cleaner look.
    - Net peaks tell a story: 2005 (+197K) WP 1.5, 2017 (-39K) cleanup, 2018 (+118K) Gutenberg


    **Next**: Transform from data display into data story.
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## Iteration 5: Add Storytelling

    **AI Prompt**: "Transform this from a data display into a data story. Add a takeaway
    title that states the key insight. Remove chart titles since inline labels provide
    context. Add WordPress milestone annotations."

    **Principles applied**: Insight-driven titles, contextual annotations, narrative framing
    """)
    return


@app.cell
def _(df, go, make_subplots):
    # Official WordPress Brand Colors
    WP_BLUE_5 = "#21759b"        # WordPress Blue - Contributors
    WP_CERULEAN_5 = "#00aadc"    # Cerulean - Lines Added
    WP_ORANGE_5 = "#d54e21"      # WordPress Orange - Lines Deleted
    WP_ORIENT_5 = "#005082"      # Orient Blue - Net Change
    WP_DARK_GRAY_5 = "#464646"   # Text color

    # Iteration 5: Full storytelling - no subplot titles
    fig5 = make_subplots(
        rows=3, cols=1,
        vertical_spacing=0.08,
        shared_xaxes=True,
        row_heights=[0.33, 0.33, 0.34]
    )

    # Contributors chart
    fig5.add_trace(
        go.Scatter(
            x=df["date"], y=df["unique_props_contributors"],
            mode="lines", line=dict(color=WP_BLUE_5, width=2),
            showlegend=False
        ),
        row=1, col=1
    )

    # Lines added - area fill
    fig5.add_trace(
        go.Scatter(
            x=df["date"], y=df["total_lines_added"],
            mode="lines",
            line=dict(color=WP_CERULEAN_5, width=1.5),
            fill="tozeroy",
            fillcolor="rgba(0, 170, 220, 0.3)",
            showlegend=False
        ),
        row=2, col=1
    )

    # Lines deleted - area fill
    fig5.add_trace(
        go.Scatter(
            x=df["date"], y=df["total_lines_deleted"],
            mode="lines",
            line=dict(color=WP_ORANGE_5, width=1.5),
            fill="tozeroy",
            fillcolor="rgba(213, 78, 33, 0.3)",
            showlegend=False
        ),
        row=2, col=1
    )

    # Net change - area fill
    fig5.add_trace(
        go.Scatter(
            x=df["date"], y=df["net_lines"],
            mode="lines",
            line=dict(color=WP_ORIENT_5, width=2),
            fill="tozeroy",
            fillcolor="rgba(0, 80, 130, 0.3)",
            showlegend=False
        ),
        row=3, col=1
    )

    # Add zero line for net change
    fig5.add_hline(y=0, line=dict(color="#999", width=1, dash="dash"), row=3, col=1)

    # Inline label for Contributors
    _last_contrib_5 = df.iloc[-1]
    fig5.add_annotation(
        x=_last_contrib_5["date"], y=_last_contrib_5["unique_props_contributors"],
        text="Contributors",
        showarrow=False,
        xshift=60,
        font=dict(color=WP_BLUE_5, size=18, weight="bold"),
        row=1, col=1
    )

    # Inline labels for Lines chart - spread vertically to avoid overlap
    _last_row_5 = df.iloc[-1]
    fig5.add_annotation(
        x=_last_row_5["date"], y=_last_row_5["total_lines_added"],
        text="Lines Added",
        showarrow=False,
        xshift=55,
        yshift=25,  # Move up
        font=dict(color=WP_CERULEAN_5, size=18, weight="bold"),
        row=2, col=1
    )
    fig5.add_annotation(
        x=_last_row_5["date"], y=_last_row_5["total_lines_deleted"],
        text="Lines Deleted",
        showarrow=False,
        xshift=65,
        yshift=-20,  # Move down
        font=dict(color=WP_ORANGE_5, size=18, weight="bold"),
        row=2, col=1
    )

    # Inline label for Net change
    fig5.add_annotation(
        x=_last_row_5["date"], y=_last_row_5["net_lines"],
        text="Net",
        showarrow=False,
        xshift=30,
        font=dict(color=WP_ORIENT_5, size=18, weight="bold"),
        row=3, col=1
    )

    # Key WordPress milestones with vertical lines and annotations
    _milestones = [
        ("2010-06-17", "WP 3.0\nMultisite"),
        ("2018-12-06", "Gutenberg\n(WP 5.0)"),
        ("2022-05-24", "WP 6.0\nFSE"),
    ]

    for _date_str, _label in _milestones:
        # Vertical line on all charts
        fig5.add_vline(
            x=_date_str, line=dict(color=WP_DARK_GRAY_5, width=1, dash="dot"),
            row=1, col=1
        )
        fig5.add_vline(
            x=_date_str, line=dict(color=WP_DARK_GRAY_5, width=1, dash="dot"),
            row=2, col=1
        )
        fig5.add_vline(
            x=_date_str, line=dict(color=WP_DARK_GRAY_5, width=1, dash="dot"),
            row=3, col=1
        )
        # Annotation only on row 1
        _y_max = df["unique_props_contributors"].max()
        fig5.add_annotation(
            x=_date_str, y=_y_max * 0.95,
            text=_label,
            showarrow=False,
            font=dict(size=13, color=WP_DARK_GRAY_5),
            bgcolor="rgba(255,255,255,0.8)",
            row=1, col=1
        )

    # Peak annotations for contributors - with dates
    # (date, value, yshift, xshift, label)
    _contributor_peaks_5 = [
        ("2007-01-01", 10, 20, 0, "10\n(Jan 2007)"),
        ("2010-04-05", 307, 20, 0, "307\n(Apr 2010)"),
        ("2013-09-16", 479, 20, 0, "479\n(Sep 2013)"),
        ("2018-10-22", 631, 20, 0, "631\n(Oct 2018)"),
    ]
    for _date_str, _contributors, _yshift, _xshift, _label in _contributor_peaks_5:
        fig5.add_annotation(
            x=_date_str, y=_contributors,
            text=_label,
            showarrow=False,
            yshift=_yshift,
            xshift=_xshift,
            font=dict(color=WP_BLUE_5, size=17, weight="bold"),
            row=1, col=1
        )

    # Peak annotations for Lines Added - key milestones only
    # (date, value, yshift, xshift)
    _lines_added_peaks_5 = [
        ("2005-04-11", 201588, 20, 0),    # WP 1.5 release
        ("2020-11-30", 227664, 24, -4),   # Peak activity
    ]
    for _date_str, _lines, _yshift, _xshift in _lines_added_peaks_5:
        fig5.add_annotation(
            x=_date_str, y=_lines,
            text=f"{_lines/1000:.0f}K",
            showarrow=False,
            yshift=_yshift,
            xshift=_xshift,
            font=dict(color=WP_CERULEAN_5, size=17, weight="bold"),
            row=2, col=1
        )

    # Peak annotations for Lines Deleted - key milestone only
    # (date, value, yshift, xshift)
    _lines_deleted_peaks_5 = [
        ("2021-01-18", 204728, 18, 4),    # Peak deletions
    ]
    for _date_str, _lines, _yshift, _xshift in _lines_deleted_peaks_5:
        fig5.add_annotation(
            x=_date_str, y=_lines,
            text=f"{_lines/1000:.0f}K",
            showarrow=False,
            yshift=_yshift,
            xshift=_xshift,
            font=dict(color=WP_ORANGE_5, size=17, weight="bold"),
            row=2, col=1
        )

    # Peak annotations for Net Change - key peaks and valleys
    # (date, value, yshift, xshift)
    _net_peaks_5 = [
        ("2005-04-18", 196637, 20, 0),     # WP 1.5 release
        ("2017-12-18", -38622, -28, 0),    # Post WP 4.9 cleanup
        ("2018-10-08", 117674, 20, 0),     # WP 5.0 Gutenberg push
        ("2020-09-28", 112182, 20, 0),   # WP 5.5/5.6 development
        ("2021-02-15", -18864, -24, 0),     # Post 5.7 refactoring
        ("2023-08-07", 101879, 20, 0),   # WP 6.3 FSE maturity
        ("2024-10-07", -16242, -20, 0),     # WP 6.7 cleanup
    ]
    for _date_str, _net, _yshift, _xshift in _net_peaks_5:
        fig5.add_annotation(
            x=_date_str, y=_net,
            text=f"{_net/1000:+.0f}K" if _net >= 0 else f"{_net/1000:.0f}K",
            showarrow=False,
            yshift=_yshift,
            xshift=_xshift,
            font=dict(color=WP_ORIENT_5, size=17, weight="bold"),
            row=3, col=1
        )

    # Layout with insight-driven title - left aligned
    fig5.update_layout(
        height=800,
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="Open Sans, sans-serif", size=15, color=WP_DARK_GRAY_5),
        showlegend=False,
        title=dict(
            text=(
                "WordPress: Two Decades of Open Source Growth<br>"
                "<span style='font-size:17px'>5M lines added and 600+ quarterly contributors at peak</span>"
            ),
            x=0, xanchor="left",
            font=dict(size=26, color=WP_DARK_GRAY_5)
        ),
        margin=dict(r=120, l=60, t=100)
    )

    # Axes styling - use ~s to avoid "0.0"
    fig5.update_xaxes(
        tickformat="%Y",
        showgrid=False,
        zeroline=False,
        tickfont=dict(color=WP_DARK_GRAY_5, size=15)
    )
    fig5.update_yaxes(
        showgrid=False,
        zeroline=False,
        tickfont=dict(color=WP_DARK_GRAY_5, size=15),
        tickformat="~s"
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
    | Legend | External box | Inline labels at line ends |
    | Context | None | Milestone annotations |
    | Layout | Side-by-side | Vertically aligned, shared x-axis |
    | Chart titles | Generic | Removed (inline labels suffice) |
    | Message | "Here's data" | "Here's what the data means" |

    The same data tells a completely different story when presented well.
    AI assistants can apply these dataviz principles systematically, making professional-quality
    charts accessible to everyone.
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## Summary Statistics
    """)
    return


@app.cell
def _(df, df_weekly, mo):
    # Calculate summary stats from weekly data (non-overlapping totals)
    total_added = df_weekly["total_lines_added"].sum()
    total_deleted = df_weekly["total_lines_deleted"].sum()
    net_growth = total_added - total_deleted
    num_weeks = len(df_weekly)

    # Peak contributor period from rolling data
    peak_contrib_row = df.loc[df["unique_props_contributors"].idxmax()]
    peak_contrib_date = peak_contrib_row["date"].strftime("%Y-%m-%d")
    peak_contributors = peak_contrib_row["unique_props_contributors"]

    # Peak lines period from rolling data
    peak_lines_row = df.loc[df["total_lines_added"].idxmax()]
    peak_lines_date = peak_lines_row["date"].strftime("%Y-%m-%d")
    peak_added = peak_lines_row["total_lines_added"]

    mo.md(f"""
    ### WordPress Code Statistics (2003-2025)

    | Metric | Value |
    |--------|-------|
    | Total lines added | {total_added:,} |
    | Total lines deleted | {total_deleted:,} |
    | Net code growth | {net_growth:,} |
    | Peak contributors (quarterly) | {int(peak_contributors):,} ({peak_contrib_date}) |
    | Peak lines added (quarterly) | {int(peak_added):,} ({peak_lines_date}) |
    | Average weekly additions | {int(total_added / num_weeks):,} |
    | Average weekly deletions | {int(total_deleted / num_weeks):,} |
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
def _(NOTEBOOK_DIR, fig0, fig1, fig2, fig3, fig4, fig5):
    import os

    # Collect all figures with their output filenames
    all_charts = {
        "fig0": (fig0, "evolution_iteration_0_weekly.png"),
        "fig1": (fig1, "evolution_iteration_1_defaults.png"),
        "fig2": (fig2, "evolution_iteration_2_decluttered.png"),
        "fig3": (fig3, "evolution_iteration_3_brand_colors.png"),
        "fig4": (fig4, "evolution_iteration_4_net_growth.png"),
        "fig5": (fig5, "evolution_iteration_5_storytelling.png"),
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
