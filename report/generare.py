from pathlib import Path

from jinja2 import Environment, FileSystemLoader, Template

from .conversii import image_to_html
from .pregatire_date import pregatire_date_raport


def get_template_html(fisier: str = "report-template.html") -> Template:
	assets_folder = Path(__file__).parent.parent / "assets" / "report"
	env = Environment(loader=FileSystemLoader(assets_folder))
	template: Template = env.get_template(fisier)
	return template


def generare_cod_raport(date_raport: dict):
	date_pregatite: dict = pregatire_date_raport(date_raport)

	template: Template = get_template_html()

	html_final = template.render(
		logo=image_to_html(Path(__file__).parent.parent / "assets" / "logo" / "logo-text-dark.png"),
		set_date=date_pregatite.get("set_date", None),
		eda=date_pregatite.get("eda", None),
		preprocesare=date_pregatite.get("preprocesare", None),
		modele_antrenate=date_pregatite.get("modele_antrenate", None),
		rezultate_modele=date_pregatite.get("rezultate_modele", None),
		comparatii_modele=date_pregatite.get("comparatii_modele", None),
		xai_test=date_pregatite.get("xai_test", None),
		xai_predictii=date_pregatite.get("xai_predictii", None),
	)

	return html_final


def generare_raport(date_raport: dict) -> bytes:
	cale_css = Path(__file__).parent.parent / "assets" / "report" / "report-style.css"
	cod_raport = generare_cod_raport(date_raport)
	with open(cale_css, "r", encoding="utf-8") as f:
		continut_css = f.read()
	style_tag = f"<style>\n{continut_css}\n</style>"
	cod_raport = cod_raport.replace("<head>", f"<head>\n{style_tag}")
	report_bytes: bytes = cod_raport.encode("utf-8")
	return report_bytes
