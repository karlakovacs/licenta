import base64

import pdfkit
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components


config = pdfkit.configuration(wkhtmltopdf="C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")


fig = go.Figure(data=go.Bar(x=["A", "B", "C"], y=[10, 20, 30]))
fig.update_layout(title="Exemplu Plotly", template="plotly_white")

img_bytes = fig.to_image(format="svg")

img_base64 = base64.b64encode(img_bytes).decode("utf-8")
html_img = f"<img src='data:image/svg+xml;base64,{img_base64}' style='width:100%;'/>"

html_page = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Grafic Exportat</title>
</head>
<body style="text-align:center;">
    <h2>Grafic Exportat în PDF</h2>
    {html_img}
</body>
</html>
"""

pdf_bytes = pdfkit.from_string(
	html_page, False, configuration=config, css="C:/Users/karla/Desktop/licenta_app/report/style.css"
)

st.subheader("✅ Grafic în pagină")
st.plotly_chart(fig, use_container_width=True)

st.subheader("🌐 HTML Static cu Imagine")
components.html(html_page, height=600)

st.download_button("⬇️ Descarcă PDF", pdf_bytes, "grafic.pdf", "application/pdf")
