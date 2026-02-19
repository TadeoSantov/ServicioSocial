"use client";

import { useState, useRef, useCallback } from "react";
import { runFullPipeline } from "@/lib/api";
import type { FullPipelineResponse, FullPipelineParams } from "@/types/api";
import { Header } from "@/components/Header";
import { Sidebar } from "@/components/Sidebar";
import { MaterialRubricSection } from "@/components/MaterialRubricSection";
import { AudioSection } from "@/components/AudioSection";
import { EvaluateButton } from "@/components/EvaluateButton";
import { ResultsPanel } from "@/components/ResultsPanel";

export interface AppConfig {
  whisperProvider: string;
  llmProvider: string;
  cleanTranscription: boolean;
  detectReading: boolean;
  language: string;
  groqApiKey: string;
  mistralApiKey: string;
  googleApiKey: string;
  azureApiKey: string;
  azureEndpoint: string;
}

export default function Home() {
  const [config, setConfig] = useState<AppConfig>({
    whisperProvider: "groq",
    llmProvider: "mistral",
    cleanTranscription: true,
    detectReading: true,
    language: "es",
    groqApiKey: "",
    mistralApiKey: "",
    googleApiKey: "",
    azureApiKey: "",
    azureEndpoint: "",
  });

  const [material, setMaterial] = useState("");
  const [rubric, setRubric] = useState("");
  const [audioFile, setAudioFile] = useState<File | Blob | null>(null);
  const [audioName, setAudioName] = useState("");
  const [audioUrl, setAudioUrl] = useState<string | null>(null);

  const [isEvaluating, setIsEvaluating] = useState(false);
  const [currentStep, setCurrentStep] = useState("");
  const [result, setResult] = useState<FullPipelineResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const [sidebarOpen, setSidebarOpen] = useState(false);

  const handleAudioSelected = useCallback((file: File | Blob, name: string) => {
    setAudioFile(file);
    setAudioName(name);
    if (audioUrl) URL.revokeObjectURL(audioUrl);
    setAudioUrl(URL.createObjectURL(file));
  }, [audioUrl]);

  const handleClearAudio = useCallback(() => {
    setAudioFile(null);
    setAudioName("");
    if (audioUrl) URL.revokeObjectURL(audioUrl);
    setAudioUrl(null);
  }, [audioUrl]);

  const handleEvaluate = async () => {
    if (!material.trim()) {
      setError("Ingresa el material de referencia");
      return;
    }
    if (!rubric.trim()) {
      setError("Ingresa la rubrica de evaluacion");
      return;
    }
    if (!audioFile) {
      setError("Sube un archivo de audio o graba uno");
      return;
    }

    setError(null);
    setIsEvaluating(true);
    setCurrentStep("Enviando audio al servidor...");
    setResult(null);

    try {
      const params: FullPipelineParams = {
        material,
        rubric,
        language: config.language,
        whisperProvider: config.whisperProvider,
        llmProvider: config.llmProvider,
        cleanTranscription: config.cleanTranscription,
        detectReading: config.detectReading,
        groqApiKey: config.groqApiKey || undefined,
        mistralApiKey: config.mistralApiKey || undefined,
        googleApiKey: config.googleApiKey || undefined,
        azureApiKey: config.azureApiKey || undefined,
        azureEndpoint: config.azureEndpoint || undefined,
      };

      setCurrentStep("Procesando evaluacion (transcripcion, analisis, calificacion)...");
      const response = await runFullPipeline(audioFile, params);

      if (!response.success) {
        setError(response.error || "Error desconocido en la evaluacion");
      } else {
        setResult(response);
      }
    } catch (err: any) {
      setError(err.message || "Error de conexion con el servidor");
    } finally {
      setIsEvaluating(false);
      setCurrentStep("");
    }
  };

  const handleNewEvaluation = () => {
    setResult(null);
    setError(null);
    handleClearAudio();
  };

  return (
    <div className="min-h-screen bg-surface-alt">
      <Header onToggleSidebar={() => setSidebarOpen(!sidebarOpen)} />

      <Sidebar
        config={config}
        onChange={setConfig}
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />

      <main className="max-w-5xl mx-auto px-4 py-6">
        {!result ? (
          <div className="space-y-6 animate-fade-in">
            <MaterialRubricSection
              material={material}
              rubric={rubric}
              onMaterialChange={setMaterial}
              onRubricChange={setRubric}
            />

            <AudioSection
              audioFile={audioFile}
              audioName={audioName}
              audioUrl={audioUrl}
              onAudioSelected={handleAudioSelected}
              onClearAudio={handleClearAudio}
            />

            <EvaluateButton
              isEvaluating={isEvaluating}
              currentStep={currentStep}
              error={error}
              onEvaluate={handleEvaluate}
            />
          </div>
        ) : (
          <div className="animate-slide-up">
            <ResultsPanel result={result} onNewEvaluation={handleNewEvaluation} />
          </div>
        )}
      </main>

      <footer className="text-center py-6 border-t border-border text-text-muted text-xs mt-8">
        <p>Whisper (Groq) &middot; Mistral Large &middot; Gemini 2.0 Flash</p>
      </footer>
    </div>
  );
}
