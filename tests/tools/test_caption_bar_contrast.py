"""La barra del subtítulo se elegía comparando el fondo con tres colores exactos.

    "rgba(255,255,255,0.85)" if bg in ("#FFFFFF","#FAFAFA","#F9FAFB") else "rgba(15,23,42,0.75)"

Los cinco playbooks de la casa pasaban porque sus fondos claros SON justo esos
tres valores. Cualquier marca con un claro propio caía a la barra oscura.

Encontrado el 9-sep-2026 al escribir el playbook de ROKEAH: su marfil #FCF1EA es
un fondo claro, pero no está en la lista, así que su texto verde oscuro #004D3F
acababa sobre la barra oscura a 1,19:1 — muy por debajo del 4,5:1 de WCAG AA.

Ahora la barra se elige MIDIENDO cuál deja el texto legible.
"""

import pytest

from styles.playbook_loader import validate_contrast
from tools.video.video_compose import VideoCompose

CLARA = "rgba(255, 255, 255, 0.85)"
OSCURA = "rgba(15, 23, 42, 0.75)"


def _sobre(bar: str, bg_hex: str) -> str:
    import re
    bg = bg_hex.lstrip("#")
    br, bgr, bb = (int(bg[i:i + 2], 16) for i in (0, 2, 4))
    r, g, b, a = (float(x) for x in re.findall(r"[\d.]+", bar))
    return "#%02X%02X%02X" % (round(r * a + br * (1 - a)),
                              round(g * a + bgr * (1 - a)),
                              round(b * a + bb * (1 - a)))


def test_el_marfil_de_rokeah_ya_no_cae_a_la_barra_oscura():
    # el caso exacto que lo destapó
    assert VideoCompose._pick_caption_bar("#004D3F", "#FCF1EA") == CLARA


def test_ese_caso_pasa_de_ilegible_a_legible():
    bar = VideoCompose._pick_caption_bar("#004D3F", "#FCF1EA")
    assert validate_contrast("#004D3F", _sobre(bar, "#FCF1EA"))["ratio"] >= 4.5
    # y con la barra que se elegía antes, no llegaba
    assert validate_contrast("#004D3F", _sobre(OSCURA, "#FCF1EA"))["ratio"] < 4.5


@pytest.mark.parametrize("bg", ["#FFFFFF", "#FAFAFA", "#F9FAFB"])
def test_los_tres_de_la_lista_vieja_eligen_lo_mismo_que_antes(bg):
    # sin regresión para los playbooks de la casa
    assert VideoCompose._pick_caption_bar("#1F2937", bg) == CLARA


@pytest.mark.parametrize("bg", ["#0A0A1A", "#0F172A", "#14130F"])
def test_los_fondos_oscuros_siguen_con_barra_oscura(bg):
    assert VideoCompose._pick_caption_bar("#F5F0E8", bg) == OSCURA



def test_color_invalido_cae_a_la_barra_oscura():
    assert VideoCompose._pick_caption_bar("#004D3F", "esto-no-es-un-color") == OSCURA
