"""El puente perdía también el gris de apoyo y el nombre del playbook.

Mismo defecto de familia que el issue #306 y con el mismo remedio: la clave del
esquema manda, la vieja se conserva como marcha atrás. Estos dos casos NO los
cubre el PR #307, por eso van aparte.

Medido el 9-sep-2026 con styles/custom/centinela.yaml: pidiendo muted #9900FF
salía #6B7280, y el DESIGN.md salía titulado "# DESIGN" sin nombre.
"""

from lib.hyperframes_style_bridge import style_bridge


def _con_paleta(**colores) -> dict:
    return {"visual_language": {"color_palette": colores}}


def test_gris_se_lee_de_la_clave_del_esquema():
    css, _ = style_bridge(_con_paleta(muted="#9900FF"))
    assert css["--color-muted"] == "#9900FF"


def test_gris_admite_todavia_la_clave_vieja():
    css, _ = style_bridge(_con_paleta(muted_text="#123456"))
    assert css["--color-muted"] == "#123456"


def test_gris_la_clave_del_esquema_gana_a_la_vieja():
    css, _ = style_bridge(_con_paleta(muted="#9900FF", muted_text="#123456"))
    assert css["--color-muted"] == "#9900FF"


def test_gris_sin_ninguna_de_las_dos_cae_al_de_fabrica():
    css, _ = style_bridge(_con_paleta(primary="#FF6600"))
    assert css["--color-muted"] == "#6B7280"


def test_nombre_se_lee_de_identity():
    _, design_md = style_bridge({"identity": {"name": "CENTINELA"}})
    assert design_md.splitlines()[0] == "# DESIGN — CENTINELA"
    assert "playbook `CENTINELA`" in design_md


def test_nombre_admite_todavia_la_raiz():
    _, design_md = style_bridge({"name": "Legacy"})
    assert design_md.splitlines()[0] == "# DESIGN — Legacy"


def test_nombre_identity_gana_a_la_raiz():
    _, design_md = style_bridge({"identity": {"name": "Nuevo"}, "name": "Viejo"})
    assert design_md.splitlines()[0] == "# DESIGN — Nuevo"


def test_sin_nombre_el_titulo_queda_pelado():
    _, design_md = style_bridge({"identity": {}})
    assert design_md.splitlines()[0] == "# DESIGN"
