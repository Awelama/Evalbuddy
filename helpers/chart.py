import streamlit as st
import pandas as pd
import altair as alt

def generate_chart(chart_type, x_data, y_data, title):
    try:
        x = [x.strip() for x in x_data.split(",")]
        y = [float(y.strip()) for y in y_data.split(",")]

        if len(x) != len(y):
            st.error("X and Y must have the same number of items.")
            return

        df = pd.DataFrame({"X": x, "Y": y})

        chart = None
        if chart_type == "Bar":
            chart = alt.Chart(df).mark_bar().encode(x='X', y='Y')
        elif chart_type == "Line":
            chart = alt.Chart(df).mark_line().encode(x='X', y='Y')
        elif chart_type == "Pie":
            st.warning("Altair does not support pie charts directly.")
            return

        if chart:
            st.altair_chart(chart.properties(title=title), use_container_width=True)

    except Exception as e:
        st.error(f"Error generating chart: {e}")
