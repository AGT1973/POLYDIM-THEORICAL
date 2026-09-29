import os

input_path = r"g:\Mi unidad\POLYDIM_v1_1\docs\constitution\POLYDIM_CONSTITUCION_FINAL_CLEAN.md"
output_path = r"g:\Mi unidad\POLYDIM_v1_1\docs\CONSTITUCION_V2.md"

with open(input_path, "r", encoding="utf-8") as f:
    content = f.read()

# Remove the old title lines
lines = content.split('\n')
start_idx = 0
for i, line in enumerate(lines):
    if line.startswith("PREÁMBULO"):
        start_idx = i
        break

old_body = '\n'.join(lines[start_idx:])

new_preamble = """# CONSTITUCIÓN OMNICOMPRENSIVA DE LA PROGRAMACIÓN COGNITIVA (V2.0)
*Evolución del Proyecto POLYDIM hacia un Programa de Investigación Científica*

## PREÁMBULO V2.0: EL NACIMIENTO DE UNA DISCIPLINA

A partir de la Fase XXXII, el paradigma de este documento evoluciona. Nuestro objeto de estudio ya no es exclusivamente construir un "lenguaje" (POLYDIM), sino fundar la disciplina científica de la **Programación Cognitiva**. 

POLYDIM queda formalmente constituido como el **primer caso de estudio matemático** y el vehículo empírico para demostrar que la capa representacional (el estado $S$, las transformaciones $T$, y el observador $O$) puede ser formalizada rigurosamente. La tupla del programa es ahora $P = (S, G, T, O, C, \Pi)$.

Todo agente de IA y desarrollador que opere bajo esta Constitución debe acatar las reglas técnicas y algebraicas de la V10.0 original (expuestas a continuación), pero reinterpretadas bajo el nuevo Teorema de Preservación Cognitiva: *No programamos secuencias algorítmicas deterministas, diseñamos procesos de razonamiento bajo restricciones y objetivos verificables.*

Adicionalmente, se instituye la **Ley de Aislamiento (Sandboxing)**: Los agentes experimentales no deben modificar este corpus teórico directamente, debiendo operar en entornos aislados (`/Alumnos/`).

---

"""

final_content = new_preamble + old_body

with open(output_path, "w", encoding="utf-8") as f:
    f.write(final_content)

print(f"Constitution successfully merged and saved to {output_path} with length {len(final_content)}")
