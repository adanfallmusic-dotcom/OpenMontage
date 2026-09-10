"""subtitle_gen troceaba solo por número de palabras y de caracteres.

Medido el 9-sep-2026 sobre LA_TORMENTA_narrado_v2.mp4 (una pieza con largos
pasajes musicales entre frases): la salida traía un rótulo de 140,6 segundos
—«ha jurado cruzarla. Creo, señor, ayuda a»— que juntaba dos frases separadas
por más de dos minutos y se quedaba fijo en pantalla todo ese rato.

Causa: _build_cues aplana las palabras de todos los segmentos en una sola lista
y solo corta por max_words / max_chars. Nunca cortaba en un silencio ni al final
de una frase.
"""

from tools.subtitle.subtitle_gen import SubtitleGen


def _seg(palabras):
    return {"start": palabras[0][1], "end": palabras[-1][2],
            "text": " ".join(p[0] for p in palabras),
            "words": [{"word": p[0], "start": p[1], "end": p[2]} for p in palabras]}


def _duraciones(cues):
    return [round(c["end"] - c["start"], 2) for c in cues]


def test_corta_en_un_silencio_largo():
    # dos palabras separadas por 100 s de música: jamás pueden ir en el mismo rótulo
    seg = _seg([("hola", 0.0, 0.5), ("adios", 100.0, 100.5)])
    cues = SubtitleGen()._build_cues([seg], max_words=8, max_chars=42, max_gap=0.7)
    assert len(cues) == 2
    assert max(_duraciones(cues)) < 1.0


def test_corta_al_terminar_la_frase():
    seg = _seg([("Uno", 0.0, 0.3), ("dos.", 0.3, 0.6), ("Tres", 0.7, 1.0)])
    cues = SubtitleGen()._build_cues([seg], max_words=8, max_chars=42, max_gap=0.7)
    assert [c["text"] for c in cues] == ["Uno dos.", "Tres"]


def test_tambien_corta_con_interrogacion_y_exclamacion():
    for fin in ("?", "!", "…"):
        seg = _seg([(f"Que{fin}", 0.0, 0.3), ("Sigue", 0.4, 0.7)])
        cues = SubtitleGen()._build_cues([seg], max_words=8, max_chars=42, max_gap=0.7)
        assert len(cues) == 2, f"no cortó tras {fin}"


def test_max_gap_cero_desactiva_el_corte_por_silencio():
    # marcha atrás: quien quiera el comportamiento viejo puede pedirlo
    seg = _seg([("hola", 0.0, 0.5), ("adios", 100.0, 100.5)])
    cues = SubtitleGen()._build_cues([seg], max_words=8, max_chars=42, max_gap=0)
    assert len(cues) == 1


def test_sigue_cortando_por_numero_de_palabras():
    pal = [(f"p{i}", i * 0.2, i * 0.2 + 0.15) for i in range(20)]
    cues = SubtitleGen()._build_cues([_seg(pal)], max_words=5, max_chars=200, max_gap=0.7)
    assert all(len(c["words"]) <= 5 for c in cues)


def test_ningun_rotulo_dura_mas_que_su_propio_habla():
    # el caso real: frases separadas por musica, como en LA TORMENTA
    segs = [
        _seg([("Si", 182.5, 182.9), ("quedo.", 182.9, 183.4)]),
        _seg([("Porque", 209.6, 210.0), ("levantarse.", 210.0, 210.6)]),
    ]
    cues = SubtitleGen()._build_cues(segs, max_words=8, max_chars=42, max_gap=0.7)
    assert max(_duraciones(cues)) < 2.0, f"rótulo demasiado largo: {_duraciones(cues)}"
