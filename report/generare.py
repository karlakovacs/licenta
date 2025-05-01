from pathlib import Path

from jinja2 import Environment, FileSystemLoader, Template
import pdfkit

from .pregatire_date import pregatire_date_raport


def get_template_html(fisier: str = "template.html") -> Template:
	template_folder = Path(__file__).parent
	env = Environment(loader=FileSystemLoader(template_folder))
	template: Template = env.get_template(fisier)
	return template


def generare_cod_raport(date_raport: dict, format_pdf: bool = False):
	date_pregatite: dict = pregatire_date_raport(date_raport, format_pdf)

	template: Template = get_template_html()

	html_final = template.render(
		set_date=date_pregatite.get("set_date"),
		eda=date_pregatite.get("eda"),
		procesare=date_pregatite.get("procesare"),
		modele_antrenate=date_pregatite.get("modele_antrenate"),
		rezultate_modele=date_pregatite.get("rezultate_modele"),
		xai=date_pregatite.get("xai"),
		grafic_comparativ=date_pregatite.get("grafic_comparativ"),
	)

	return html_final


def generare_raport(date_raport: dict, format_pdf: bool = False, fisier_css: str = "report/style.css") -> bytes:
	cod_raport = generare_cod_raport(date_raport, format_pdf)
	if not format_pdf:
		with open(fisier_css, "r", encoding="utf-8") as f:
			continut_css = f.read()
		style_tag = f"<style>\n{continut_css}\n</style>"
		cod_raport = cod_raport.replace("<head>", f"<head>\n{style_tag}")
		report_bytes: bytes = cod_raport.encode("utf-8")
	else:
		report_bytes: bytes = pdfkit.from_string(
			cod_raport,
			False,
			configuration=pdfkit.configuration(wkhtmltopdf="C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe"),
			css=fisier_css,
		)
	return report_bytes
