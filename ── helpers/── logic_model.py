import streamlit as st
import graphviz

def generate_logic_model(inputs, activities, outputs, outcomes, impact):
    dot = graphviz.Digraph()
    dot.attr(rankdir='LR')

    def add_node(label, content):
        content = content.strip() or "N/A"
        dot.node(label, f"<<b>{label}</b><br/>{content}>>", shape="box")

    add_node("Inputs", inputs)
    add_node("Activities", activities)
    add_node("Outputs", outputs)
    add_node("Outcomes", outcomes)
    add_node("Impact", impact)

    dot.edges([
        ("Inputs", "Activities"),
        ("Activities", "Outputs"),
        ("Outputs", "Outcomes"),
        ("Outcomes", "Impact")
    ])

    st.graphviz_chart(dot)
