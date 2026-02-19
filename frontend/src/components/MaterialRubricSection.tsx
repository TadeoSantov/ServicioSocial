"use client";

import { BookOpen, ClipboardList, FlaskConical } from "lucide-react";

const EJEMPLOS: Record<string, { material: string; rubric: string }> = {
  ratatouille: {
    material: `Ratatouille es una pelicula de animacion de Pixar (2007) dirigida por Brad Bird. Narra la historia de Remy, una rata con un extraordinario sentido del olfato y del gusto que suena con convertirse en chef en Paris. Remy se asocia con Linguini, un joven torpey sin talento culinario, para cocinar en el restaurante Gusteau's. El titulo hace referencia al plato provenzal frances "ratatouille", una preparacion de verduras salteadas. Los temas principales son: perseguir los suenos a pesar de las limitaciones sociales, la autenticidad en el arte, y la idea de que "cualquiera puede cocinar" (Anyone can cook). El antagonista es el critico gastronomico Anton Ego, cuya resena puede destruir o salvar el restaurante. Al final, Remy prepara una ratatouille que transporta a Ego a su infancia, logrando una critica positiva. La pelicula ganó el Oscar a Mejor Pelicula Animada en 2008.`,
    rubric: `Criterios de evaluacion (10 puntos total):
1. Identificacion correcta del director y estudio (1 pt)
2. Descripcion del personaje principal Remy y su sueno (2 pts)
3. Explicacion de la relacion Remy-Linguini (1.5 pts)
4. Mencion de los temas principales de la pelicula (2 pts)
5. Rol del antagonista Anton Ego (1.5 pts)
6. Desenlace y significado del plato ratatouille (1 pt)
7. Dato adicional relevante (Oscar, fecha, etc.) (1 pt)

Penalizaciones:
- Error factual grave: -1 pt
- Informacion inventada: -0.5 pt por item`,
  },
};

interface Props {
  material: string;
  rubric: string;
  onMaterialChange: (v: string) => void;
  onRubricChange: (v: string) => void;
}

export function MaterialRubricSection({
  material,
  rubric,
  onMaterialChange,
  onRubricChange,
}: Props) {
  const handleExample = (e: { target: { value: string } }) => {
    const key = e.target.value;
    if (key && EJEMPLOS[key]) {
      onMaterialChange(EJEMPLOS[key].material);
      onRubricChange(EJEMPLOS[key].rubric);
    } else {
      onMaterialChange("");
      onRubricChange("");
    }
  };

  return (
    <div className="space-y-3">
      {/* Example selector */}
      <div className="bg-white rounded-lg border border-border p-3 flex items-center gap-3">
        <FlaskConical className="w-4 h-4 text-accent shrink-0" />
        <label className="text-xs font-medium text-text-muted shrink-0">Ejemplo predefinido:</label>
        <select
          onChange={handleExample}
          defaultValue=""
          className="flex-1 px-2 py-1.5 text-sm border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-accent/30"
        >
          <option value="">-- Ninguno --</option>
          <option value="ratatouille">Ratatouille (Pixar)</option>
        </select>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Material */}
        <div className="bg-white rounded-lg border border-border p-4">
          <div className="flex items-center gap-2 mb-3">
            <BookOpen className="w-4 h-4 text-accent" />
            <h3 className="text-xs font-semibold uppercase tracking-wider text-text-primary">
              Material de referencia
            </h3>
          </div>
          <p className="text-xs text-text-muted mb-3">
            Contenido que el alumno debe dominar
          </p>
          <textarea
            value={material}
            onChange={(e) => onMaterialChange(e.target.value)}
            placeholder="Pega aqui el contenido del tema a evaluar..."
            rows={10}
            className="w-full px-3 py-2 text-sm border border-border rounded-md resize-none focus:outline-none focus:ring-2 focus:ring-accent/30 placeholder:text-text-muted/50"
          />
        </div>

        {/* Rubric */}
        <div className="bg-white rounded-lg border border-border p-4">
          <div className="flex items-center gap-2 mb-3">
            <ClipboardList className="w-4 h-4 text-accent" />
            <h3 className="text-xs font-semibold uppercase tracking-wider text-text-primary">
              Rubrica de evaluacion
            </h3>
          </div>
          <p className="text-xs text-text-muted mb-3">
            Criterios y puntos para calificar
          </p>
          <textarea
            value={rubric}
            onChange={(e) => onRubricChange(e.target.value)}
            placeholder="Define los criterios de evaluacion y su puntaje..."
            rows={10}
            className="w-full px-3 py-2 text-sm border border-border rounded-md resize-none focus:outline-none focus:ring-2 focus:ring-accent/30 placeholder:text-text-muted/50"
          />
        </div>
      </div>
    </div>
  );
}
