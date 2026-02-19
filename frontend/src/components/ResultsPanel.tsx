"use client";

import { useState } from "react";
import {
  ArrowLeft, Award, BarChart3, BookOpen, AlertTriangle,
  CheckCircle, XCircle, MessageSquare, GraduationCap,
  FileText, Download, ChevronDown, ChevronUp,
} from "lucide-react";
import type { FullPipelineResponse } from "@/types/api";
import { getGradeColor, getGradeBg, getQualityColor, getQualityLabel, formatDuration } from "@/lib/utils";

interface Props {
  result: FullPipelineResponse;
  onNewEvaluation: () => void;
}

export function ResultsPanel({ result, onNewEvaluation }: Props) {
  const [activeTab, setActiveTab] = useState(0);

  if (!result.evaluation) {
    return (
      <div className="bg-white rounded-lg border border-border p-8 text-center space-y-4">
        <XCircle className="w-12 h-12 text-red-400 mx-auto" />
        <p className="text-text-primary font-medium">La evaluacion no pudo completarse</p>
        <p className="text-text-muted text-sm">{result.error || "Error desconocido"}</p>
        <button onClick={onNewEvaluation} className="px-4 py-2 bg-accent text-white rounded-lg text-sm hover:bg-accent/90 transition-colors">
          Intentar de nuevo
        </button>
      </div>
    );
  }

  const ev = result.evaluation;

  const tabs = [
    { label: "Feedback alumno", icon: MessageSquare },
    { label: "Nota docente", icon: GraduationCap },
    { label: "Desglose", icon: BarChart3 },
    { label: "Conceptos", icon: BookOpen },
    { label: "Errores", icon: AlertTriangle },
    { label: "Transcripcion", icon: FileText },
  ];

  return (
    <div className="space-y-4">
      {/* Metrics Row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <MetricCard
          label="Calificacion final"
          value={`${ev.final_grade}/10`}
          sub={`Confianza: ${ev.confidence_level}`}
          className={getGradeBg(ev.final_grade)}
        />
        <MetricCard
          label="Cobertura de conceptos"
          value={`${ev.conceptual_analysis.coverage_percentage}%`}
        />
        <MetricCard
          label="Duracion"
          value={result.audio_duration ? formatDuration(result.audio_duration) : `${result.cleaned_transcription?.split(" ").length || 0} palabras`}
        />
        <MetricCard
          label="Tema detectado"
          value={ev.detected_topic}
          sub={`Nivel: ${ev.difficulty_level}`}
        />
      </div>

      {/* Reading Pattern Alert */}
      <ReadingAlert pattern={result.reading_pattern} />

      {/* Communication Metrics */}
      <div className="grid grid-cols-3 gap-3">
        <QualityBadge label="Claridad" value={ev.communication_metrics.clarity} />
        <QualityBadge label="Coherencia" value={ev.communication_metrics.coherence} />
        <QualityBadge label="Vocabulario tecnico" value={ev.communication_metrics.technical_vocabulary} />
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-lg border border-border overflow-hidden">
        <div className="flex overflow-x-auto border-b border-border bg-surface-alt">
          {tabs.map((tab, i) => (
            <button
              key={i}
              onClick={() => setActiveTab(i)}
              className={`flex items-center gap-1.5 px-4 py-2.5 text-xs font-medium whitespace-nowrap transition-colors border-b-2 ${
                activeTab === i
                  ? "border-accent text-accent bg-white"
                  : "border-transparent text-text-muted hover:text-text-primary"
              }`}
            >
              <tab.icon className="w-3.5 h-3.5" />
              {tab.label}
            </button>
          ))}
        </div>

        <div className="p-5">
          {activeTab === 0 && <StudentFeedbackTab ev={ev} />}
          {activeTab === 1 && <TeacherNotesTab ev={ev} />}
          {activeTab === 2 && <BreakdownTab ev={ev} />}
          {activeTab === 3 && <ConceptsTab ev={ev} />}
          {activeTab === 4 && <ErrorsTab ev={ev} />}
          {activeTab === 5 && <TranscriptionTab result={result} ev={ev} />}
        </div>
      </div>

      {/* New Evaluation Button */}
      <button
        onClick={onNewEvaluation}
        className="w-full py-3 border border-border rounded-lg text-sm font-medium text-text-primary hover:bg-surface-alt transition-colors flex items-center justify-center gap-2"
      >
        <ArrowLeft className="w-4 h-4" />
        Nueva evaluacion
      </button>
    </div>
  );
}

/* ── Sub-components ──────────────────────────────────────────────────────── */

function MetricCard({ label, value, sub, className = "" }: { label: string; value: string; sub?: string; className?: string }) {
  return (
    <div className={`bg-white rounded-lg border border-border p-3 ${className}`}>
      <p className="text-xs text-text-muted mb-1">{label}</p>
      <p className="text-lg font-semibold text-text-primary">{value}</p>
      {sub && <p className="text-xs text-text-muted mt-0.5">{sub}</p>}
    </div>
  );
}

function QualityBadge({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-white rounded-lg border border-border p-3 text-center">
      <p className="text-xs text-text-muted mb-1">{label}</p>
      <p className={`text-sm font-semibold ${getQualityColor(value)}`}>
        {getQualityLabel(value)}
      </p>
    </div>
  );
}

function ReadingAlert({ pattern }: { pattern?: any }) {
  if (!pattern) return null;
  const probLectura = pattern.probabilidad_lectura || 0;
  const probIA = pattern.probabilidad_ia || 0;
  const esIA = pattern.es_ia_generada || false;
  const [open, setOpen] = useState(false);

  if (esIA || probIA >= 60) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <div className="flex items-start gap-2">
          <XCircle className="w-5 h-5 text-danger flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <p className="text-sm font-semibold text-danger">
              Audio generado por IA detectado — {probIA}% de probabilidad
            </p>
            <p className="text-xs text-red-700 mt-1">
              {pattern.recomendacion || "Solicitar que el alumno repita el examen de forma presencial"}
            </p>
            <button onClick={() => setOpen(!open)} className="text-xs text-red-600 mt-2 flex items-center gap-1 hover:underline">
              {open ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
              {open ? "Ocultar detalles" : "Ver detalles"}
            </button>
            {open && <p className="text-xs text-red-700 mt-2">{pattern.analisis_detallado}</p>}
          </div>
        </div>
      </div>
    );
  }

  if (probLectura >= 70 || pattern.esta_leyendo) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <div className="flex items-start gap-2">
          <AlertTriangle className="w-5 h-5 text-danger flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-semibold text-danger">
              Posible lectura detectada — {probLectura}% de probabilidad
            </p>
            <p className="text-xs text-red-700 mt-1">{pattern.recomendacion}</p>
          </div>
        </div>
      </div>
    );
  }

  if (probLectura >= 40 || probIA >= 30) {
    return (
      <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
        <div className="flex items-start gap-2">
          <AlertTriangle className="w-5 h-5 text-warning flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-semibold text-warning">
              Advertencia moderada — Lectura: {probLectura}% | IA: {probIA}%
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-4">
      <div className="flex items-start gap-2">
        <CheckCircle className="w-5 h-5 text-success flex-shrink-0 mt-0.5" />
        <p className="text-sm font-semibold text-success">
          Habla natural detectada — {100 - Math.max(probLectura, probIA)}% de confianza
        </p>
      </div>
    </div>
  );
}

function StudentFeedbackTab({ ev }: { ev: any }) {
  const fb = ev.student_feedback || {};
  return (
    <div className="space-y-4">
      {fb.resumen && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
          <p className="text-sm font-medium text-accent">Resumen del desempeno</p>
          <p className="text-sm text-blue-800 mt-1">{fb.resumen}</p>
        </div>
      )}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <h4 className="text-xs font-semibold uppercase tracking-wider text-text-primary mb-2">Fortalezas</h4>
          {(fb.fortalezas || []).length > 0 ? (
            fb.fortalezas.map((f: string, i: number) => (
              <div key={i} className="bg-emerald-50 border border-emerald-200 rounded p-2 mb-1.5 text-sm text-emerald-800">{f}</div>
            ))
          ) : (
            <p className="text-xs text-text-muted">No se identificaron fortalezas especificas</p>
          )}
        </div>
        <div>
          <h4 className="text-xs font-semibold uppercase tracking-wider text-text-primary mb-2">Areas de mejora</h4>
          {(fb.areas_mejora || []).length > 0 ? (
            fb.areas_mejora.map((a: string, i: number) => (
              <div key={i} className="bg-amber-50 border border-amber-200 rounded p-2 mb-1.5 text-sm text-amber-800">{a}</div>
            ))
          ) : (
            <p className="text-xs text-text-muted">No se identificaron areas de mejora</p>
          )}
        </div>
      </div>
      {(fb.recomendaciones_estudio || []).length > 0 && (
        <div>
          <h4 className="text-xs font-semibold uppercase tracking-wider text-text-primary mb-2">Recomendaciones de estudio</h4>
          <ul className="space-y-1">
            {fb.recomendaciones_estudio.map((r: string, i: number) => (
              <li key={i} className="text-sm text-text-primary">• {r}</li>
            ))}
          </ul>
        </div>
      )}
      {fb.mensaje_motivacional && (
        <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-3">
          <p className="text-sm text-emerald-800 font-medium">{fb.mensaje_motivacional}</p>
        </div>
      )}
    </div>
  );
}

function TeacherNotesTab({ ev }: { ev: any }) {
  const tn = ev.teacher_notes || {};
  return (
    <div className="space-y-4">
      <div>
        <h4 className="text-xs font-semibold uppercase tracking-wider text-text-primary mb-2">Observaciones generales</h4>
        <p className="text-sm text-text-primary">{tn.observaciones || "No disponible"}</p>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <h4 className="text-xs font-semibold uppercase tracking-wider text-text-primary mb-2">Patron de errores</h4>
          {tn.patron_errores ? (
            <div className="bg-amber-50 border border-amber-200 rounded p-2 text-sm text-amber-800">{tn.patron_errores}</div>
          ) : (
            <p className="text-xs text-text-muted">No se detecto un patron especifico</p>
          )}
        </div>
        <div>
          <h4 className="text-xs font-semibold uppercase tracking-wider text-text-primary mb-2">Sugerencia de refuerzo</h4>
          {tn.sugerencia_refuerzo ? (
            <div className="bg-blue-50 border border-blue-200 rounded p-2 text-sm text-blue-800">{tn.sugerencia_refuerzo}</div>
          ) : (
            <p className="text-xs text-text-muted">Sin sugerencias adicionales</p>
          )}
        </div>
      </div>
      {tn.comparacion_esperado && (
        <div>
          <h4 className="text-xs font-semibold uppercase tracking-wider text-text-primary mb-2">Comparacion con lo esperado</h4>
          <p className="text-sm text-text-primary">{tn.comparacion_esperado}</p>
        </div>
      )}
    </div>
  );
}

function BreakdownTab({ ev }: { ev: any }) {
  const bd = ev.grade_breakdown || {};
  const criteria = bd.by_criteria || [];
  const penalties = bd.penalties || [];
  const bonuses = bd.bonuses || [];

  return (
    <div className="space-y-4">
      <div>
        <h4 className="text-xs font-semibold uppercase tracking-wider text-text-primary mb-3">Calificacion por criterio</h4>
        {criteria.length > 0 ? (
          criteria.map((c: any, i: number) => {
            const pct = c.maximo > 0 ? (c.puntaje / c.maximo) * 100 : 0;
            return (
              <div key={i} className="mb-3">
                <div className="flex justify-between text-sm mb-1">
                  <span className="font-medium">{c.criterio}</span>
                  <span className="text-text-muted">{c.puntaje}/{c.maximo} pts</span>
                </div>
                <div className="w-full bg-gray-100 rounded-full h-2">
                  <div className="bg-accent h-2 rounded-full transition-all" style={{ width: `${Math.min(pct, 100)}%` }} />
                </div>
                {c.justificacion && <p className="text-xs text-text-muted mt-0.5">{c.justificacion}</p>}
              </div>
            );
          })
        ) : (
          <p className="text-xs text-text-muted">No hay desglose por criterio disponible</p>
        )}
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <h4 className="text-xs font-semibold uppercase tracking-wider text-text-primary mb-2">Penalizaciones</h4>
          {penalties.length > 0 ? (
            penalties.map((p: any, i: number) => (
              <div key={i} className="bg-red-50 border border-red-200 rounded p-2 mb-1.5 text-sm text-red-800">
                <strong>-{p.puntos_restados} pts:</strong> {p.razon}
              </div>
            ))
          ) : (
            <div className="bg-emerald-50 border border-emerald-200 rounded p-2 text-sm text-emerald-800">Sin penalizaciones</div>
          )}
        </div>
        <div>
          <h4 className="text-xs font-semibold uppercase tracking-wider text-text-primary mb-2">Bonificaciones</h4>
          {bonuses.length > 0 ? (
            bonuses.map((b: any, i: number) => (
              <div key={i} className="bg-emerald-50 border border-emerald-200 rounded p-2 mb-1.5 text-sm text-emerald-800">
                <strong>+{b.puntos_agregados} pts:</strong> {b.razon}
              </div>
            ))
          ) : (
            <p className="text-xs text-text-muted">Sin bonificaciones</p>
          )}
        </div>
      </div>
      {bd.justification && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
          <p className="text-xs font-semibold uppercase tracking-wider text-text-primary mb-1">Justificacion general</p>
          <p className="text-sm text-blue-800">{bd.justification}</p>
        </div>
      )}
    </div>
  );
}

function ConceptsTab({ ev }: { ev: any }) {
  const ca = ev.conceptual_analysis || {};
  const expected = ca.expected_concepts || {};
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <h4 className="text-xs font-semibold uppercase tracking-wider text-text-primary mb-2">Conceptos principales esperados</h4>
          {(expected.principales || []).length > 0 ? (
            <ul className="space-y-1">{expected.principales.map((p: string, i: number) => <li key={i} className="text-sm">• {p}</li>)}</ul>
          ) : <p className="text-xs text-text-muted">No definidos</p>}
        </div>
        <div>
          <h4 className="text-xs font-semibold uppercase tracking-wider text-text-primary mb-2">Conceptos secundarios</h4>
          {(expected.secundarios || []).length > 0 ? (
            <ul className="space-y-1">{expected.secundarios.map((s: string, i: number) => <li key={i} className="text-sm">• {s}</li>)}</ul>
          ) : <p className="text-xs text-text-muted">No definidos</p>}
        </div>
      </div>
      <hr className="border-border" />
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <h4 className="text-xs font-semibold uppercase tracking-wider text-text-primary mb-2">Mencionados correctamente</h4>
          {(ca.mentioned_concepts || []).length > 0 ? (
            ca.mentioned_concepts.map((m: string, i: number) => (
              <div key={i} className="bg-emerald-50 border border-emerald-200 rounded p-2 mb-1.5 text-sm text-emerald-800">{m}</div>
            ))
          ) : <p className="text-xs text-text-muted">No se identificaron conceptos correctos</p>}
        </div>
        <div>
          <h4 className="text-xs font-semibold uppercase tracking-wider text-text-primary mb-2">Conceptos omitidos</h4>
          {(ca.omitted_concepts || []).length > 0 ? (
            ca.omitted_concepts.map((o: string, i: number) => (
              <div key={i} className="bg-red-50 border border-red-200 rounded p-2 mb-1.5 text-sm text-red-800">{o}</div>
            ))
          ) : <div className="bg-emerald-50 border border-emerald-200 rounded p-2 text-sm text-emerald-800">No se omitieron conceptos importantes</div>}
        </div>
      </div>
      {(ev.highlighted_quotes || []).length > 0 && (
        <div>
          <h4 className="text-xs font-semibold uppercase tracking-wider text-text-primary mb-2">Citas destacadas del alumno</h4>
          {ev.highlighted_quotes.map((q: string, i: number) => (
            <div key={i} className="bg-blue-50 border border-blue-200 rounded p-2 mb-1.5 text-sm text-blue-800 italic">&ldquo;{q}&rdquo;</div>
          ))}
        </div>
      )}
    </div>
  );
}

function ErrorsTab({ ev }: { ev: any }) {
  const errs = ev.detected_errors || {};
  return (
    <div className="space-y-4">
      <div>
        <h4 className="text-xs font-semibold uppercase tracking-wider text-text-primary mb-2">Errores factuales</h4>
        {(errs.factual || []).length > 0 ? (
          errs.factual.map((e: any, i: number) => (
            <Collapsible key={i} title={`[${(e.gravedad || "moderado").toUpperCase()}] ${e.error?.slice(0, 60)}...`}>
              <p className="text-sm"><strong>Descripcion:</strong> {e.error}</p>
              <p className="text-sm"><strong>Gravedad:</strong> {(e.gravedad || "moderado").toUpperCase()}</p>
              {e.cita_alumno && <p className="text-sm"><strong>El alumno dijo:</strong> &ldquo;{e.cita_alumno}&rdquo;</p>}
            </Collapsible>
          ))
        ) : (
          <div className="bg-emerald-50 border border-emerald-200 rounded p-2 text-sm text-emerald-800">No se detectaron errores factuales</div>
        )}
      </div>
      <div>
        <h4 className="text-xs font-semibold uppercase tracking-wider text-text-primary mb-2">Informacion inventada</h4>
        {(errs.fabricated || []).length > 0 ? (
          errs.fabricated.map((inv: string, i: number) => (
            <div key={i} className="bg-red-50 border border-red-200 rounded p-2 mb-1.5 text-sm text-red-800">{inv}</div>
          ))
        ) : (
          <div className="bg-emerald-50 border border-emerald-200 rounded p-2 text-sm text-emerald-800">No se detecto informacion inventada</div>
        )}
      </div>
    </div>
  );
}

function TranscriptionTab({ result, ev }: { result: FullPipelineResponse; ev: any }) {
  const handleDownload = () => {
    const data = JSON.stringify(ev, null, 2);
    const blob = new Blob([data], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "evaluacion_examen.json";
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-4">
      <div>
        <h4 className="text-xs font-semibold uppercase tracking-wider text-text-primary mb-2">Transcripcion original (Whisper)</h4>
        <textarea
          readOnly
          value={result.original_transcription || ""}
          rows={6}
          className="w-full px-3 py-2 text-sm border border-border rounded-md bg-surface-alt resize-none"
        />
      </div>
      <div>
        <h4 className="text-xs font-semibold uppercase tracking-wider text-text-primary mb-2">Transcripcion procesada</h4>
        <textarea
          readOnly
          value={result.cleaned_transcription || ""}
          rows={6}
          className="w-full px-3 py-2 text-sm border border-border rounded-md bg-surface-alt resize-none"
        />
      </div>
      <button
        onClick={handleDownload}
        className="flex items-center gap-2 px-4 py-2 border border-border rounded-lg text-sm font-medium text-text-primary hover:bg-surface-alt transition-colors"
      >
        <Download className="w-4 h-4" />
        Descargar evaluacion (JSON)
      </button>
    </div>
  );
}

function Collapsible({ title, children }: { title: string; children: React.ReactNode }) {
  const [open, setOpen] = useState(false);
  return (
    <div className="border border-border rounded-lg mb-2 overflow-hidden">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between px-3 py-2 text-sm font-medium text-text-primary hover:bg-surface-alt transition-colors"
      >
        <span className="text-left">{title}</span>
        {open ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
      </button>
      {open && <div className="px-3 pb-3 space-y-1">{children}</div>}
    </div>
  );
}
