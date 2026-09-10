"""auto_reframe aceptaba cualquier target_aspect y degradaba en silencio.

Medido el 9-sep-2026 recortando LA_TORMENTA a vertical: pedir target_aspect
"9:16" —que suena al nombre obvio, pero NO es un preajuste; el de 9:16 se llama
"portrait"— devolvía success=True y un archivo de 606x1080 en vez de 1080x1920.
Un valor inventado ("BASURA-4711") daba exactamente lo mismo.

Causa de fondo: BaseTool declara input_schema pero nunca lo valida, así que el
enum del esquema no se cumple en ninguna parte. Esta guarda es local a esta
herramienta; el problema general sigue abierto.
"""

import pytest

from tools.video.auto_reframe import ASPECT_PRESETS, AutoReframe


@pytest.mark.parametrize("malo", ["9:16", "16:9", "BASURA-4711", "vertical", ""])
def test_rechaza_un_preajuste_que_no_existe(tmp_path, malo):
    v = tmp_path / "e.mp4"
    v.write_bytes(b"x")  # no llega a leerlo: la guarda va antes
    r = AutoReframe().execute({"input_path": str(v), "target_aspect": malo})
    assert r.success is False
    assert "target_aspect" in (r.error or "")


def test_el_error_dice_cual_usar():
    r = AutoReframe().execute({"input_path": "/no/existe.mp4", "target_aspect": "9:16"})
    assert "portrait" in (r.error or ""), "el error debe nombrar el preajuste correcto"


def test_los_preajustes_reales_pasan_la_guarda():
    # no deben fallar POR la guarda; fallarán luego por el archivo inexistente
    for bueno in ASPECT_PRESETS:
        r = AutoReframe().execute({"input_path": "/no/existe.mp4", "target_aspect": bueno})
        assert "Unknown target_aspect" not in (r.error or ""), bueno


def test_el_tamano_explicito_sigue_mandando_sobre_el_preajuste():
    # quien pasa medidas concretas no necesita un preajuste válido
    r = AutoReframe().execute({"input_path": "/no/existe.mp4", "target_aspect": "9:16",
                               "target_width": 1080, "target_height": 1920})
    assert "Unknown target_aspect" not in (r.error or "")
