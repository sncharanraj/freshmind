# dashboard.py — FreshMind v2.0
# Full Chart.js animated dashboard

import streamlit as st
import streamlit.components.v1 as components
from datetime import date, datetime


def render_dashboard(all_items, expiring_items,
                     history, dark_mode=False):
    """
    Renders the full animated dashboard.

    Parameters:
        all_items      : all pantry items from DB
        expiring_items : items expiring within 7 days
        history        : usage history from DB
        dark_mode      : bool for theme
    """

    t = {
        "bg":    "#1a1a2e" if dark_mode else "#ffffff",
        "text":  "#ffffff" if dark_mode else "#1a1a2e",
        "sub":   "#a0a0b0" if dark_mode else "#666666",
        "card":  "#16213e" if dark_mode else "#f8fffe",
        "border":"#2a2a4a" if dark_mode else "#e0e8f0",
    }

    st.markdown("""
        <div class='hero-banner fade-in'
             style='padding:20px 25px;'>
            <h2 style='margin:0;'>📊 Dashboard</h2>
            <p style='margin:4px 0 0; opacity:0.85;'>
                Your pantry insights & analytics
            </p>
        </div>
    """, unsafe_allow_html=True)

    # ── Compute Data ──
    categories = {}
    for item in all_items:
        cat = item['category']
        categories[cat] = categories.get(cat, 0) + 1

    # Expiry breakdown
    critical = sum(
        1 for i in all_items
        if (datetime.strptime(i['expiry_date'], "%Y-%m-%d").date()
            - date.today()).days <= 3
    )
    expiring_week = len(expiring_items)
    fresh = len(all_items) - expiring_week

    # Waste vs saved
    saved  = sum(1 for h in history if not h['was_wasted'])
    wasted = sum(1 for h in history if h['was_wasted'])

    # Category chart data
    cat_labels = list(categories.keys())
    cat_values = list(categories.values())

    if not all_items:
        st.info("📦 Add items to your pantry to see analytics!")
        return

    # ── Full JS Dashboard ──
    components.html(f"""
        <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>

        <style>
            * {{ font-family: 'Poppins', sans-serif;
                 box-sizing: border-box; margin: 0; }}
            body {{
                background: transparent;
                color: {t['text']};
            }}
            .grid2 {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
                margin-bottom: 20px;
            }}
            .grid3 {{
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 16px;
                margin-bottom: 20px;
            }}
            .card {{
                background: {t['bg']};
                border-radius: 16px;
                padding: 20px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.08);
                border: 1px solid {t['border']};
            }}
            .stat-card {{
                background: {t['bg']};
                border-radius: 16px;
                padding: 20px;
                text-align: center;
                box-shadow: 0 4px 20px rgba(0,0,0,0.08);
                border: 1px solid {t['border']};
                transition: transform 0.2s;
            }}
            .stat-card:hover {{ transform: translateY(-4px); }}
            .stat-num {{
                font-size: 2rem;
                font-weight: 700;
            }}
            .stat-label {{
                font-size: 0.78rem;
                color: {t['sub']};
                margin-top: 4px;
            }}
            h3 {{
                font-size: 1rem;
                margin-bottom: 16px;
                color: {t['text']};
            }}
        </style>

        <!-- Stat Cards -->
        <div class="grid3">
            <div class="stat-card">
                <div style="font-size:2rem">📦</div>
                <div class="stat-num" style="color:#667eea"
                     id="s1">0</div>
                <div class="stat-label">Total Items</div>
            </div>
            <div class="stat-card">
                <div style="font-size:2rem">✅</div>
                <div class="stat-num" style="color:#43e97b"
                     id="s2">0</div>
                <div class="stat-label">Items Saved</div>
            </div>
            <div class="stat-card">
                <div style="font-size:2rem">🗑️</div>
                <div class="stat-num" style="color:#f44336"
                     id="s3">0</div>
                <div class="stat-label">Items Wasted</div>
            </div>
        </div>

        <!-- Charts Row -->
        <div class="grid2">
            <!-- Category Chart -->
            <div class="card">
                <h3>🏷️ Items by Category</h3>
                <canvas id="catChart"></canvas>
            </div>

            <!-- Expiry Status Chart -->
            <div class="card">
                <h3>📅 Expiry Status</h3>
                <canvas id="expiryChart"></canvas>
            </div>
        </div>

        <!-- Waste Chart -->
        <div class="card" style="margin-bottom:20px">
            <h3>♻️ Saved vs Wasted</h3>
            <canvas id="wasteChart" height="80"></canvas>
        </div>

        <script>
            // Count up animation
            function countUp(id, target, color, duration=1500) {{
                const el = document.getElementById(id);
                let start = 0;
                const step = target / (duration / 16);
                const timer = setInterval(() => {{
                    start += step;
                    if (start >= target) {{
                        el.textContent = target;
                        clearInterval(timer);
                    }} else {{
                        el.textContent = Math.floor(start);
                    }}
                }}, 16);
            }}
            countUp('s1', {len(all_items)});
            countUp('s2', {saved});
            countUp('s3', {wasted});

            // Category Doughnut
            new Chart(document.getElementById('catChart'), {{
                type: 'doughnut',
                data: {{
                    labels: {cat_labels},
                    datasets: [{{
                        data: {cat_values},
                        backgroundColor: [
                            '#667eea','#f093fb','#4facfe',
                            '#43e97b','#fa709a','#fee140',
                            '#a18cd1','#fccb90'
                        ],
                        borderWidth: 0,
                        hoverOffset: 8
                    }}]
                }},
                options: {{
                    responsive: true,
                    plugins: {{
                        legend: {{
                            position: 'bottom',
                            labels: {{
                                color: '{t["text"]}',
                                padding: 12,
                                font: {{ size: 11 }}
                            }}
                        }}
                    }},
                    animation: {{
                        animateScale: true,
                        duration: 1500
                    }}
                }}
            }});

            // Expiry Bar Chart
            new Chart(document.getElementById('expiryChart'), {{
                type: 'bar',
                data: {{
                    labels: ['🔴 Critical', '🟠 This Week', '🟢 Fresh'],
                    datasets: [{{
                        label: 'Items',
                        data: [{critical}, {expiring_week}, {fresh}],
                        backgroundColor: ['#f44336','#ff9800','#43e97b'],
                        borderRadius: 10,
                        borderWidth: 0
                    }}]
                }},
                options: {{
                    responsive: true,
                    plugins: {{
                        legend: {{ display: false }}
                    }},
                    animation: {{ duration: 1500 }},
                    scales: {{
                        y: {{
                            beginAtZero: true,
                            grid: {{ color: '{t["border"]}' }},
                            ticks: {{ color: '{t["sub"]}' }}
                        }},
                        x: {{
                            grid: {{ display: false }},
                            ticks: {{ color: '{t["sub"]}' }}
                        }}
                    }}
                }}
            }});

            // Waste vs Saved Bar Chart
            new Chart(document.getElementById('wasteChart'), {{
                type: 'bar',
                data: {{
                    labels: ['Items Saved ✅', 'Items Wasted 🗑️'],
                    datasets: [{{
                        data: [{saved}, {wasted}],
                        backgroundColor: ['#43e97b', '#f44336'],
                        borderRadius: 10,
                        borderWidth: 0
                    }}]
                }},
                options: {{
                    indexAxis: 'y',
                    responsive: true,
                    plugins: {{
                        legend: {{ display: false }}
                    }},
                    animation: {{ duration: 1800 }},
                    scales: {{
                        x: {{
                            beginAtZero: true,
                            grid: {{ color: '{t["border"]}' }},
                            ticks: {{ color: '{t["sub"]}' }}
                        }},
                        y: {{
                            grid: {{ display: false }},
                            ticks: {{ color: '{t["sub"]}' }}
                        }}
                    }}
                }}
            }});
        </script>
    """, height=900)