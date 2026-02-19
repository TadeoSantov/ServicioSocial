"use client";

import { X, KeyRound, CheckCircle, AlertCircle } from "lucide-react";
import { useState } from "react";
import type { AppConfig } from "@/app/page";

interface SidebarProps {
  config: AppConfig;
  onChange: (config: AppConfig) => void;
  isOpen: boolean;
  onClose: () => void;
}

const LANGUAGES = [
  { value: "es", label: "Espanol" },
  { value: "en", label: "English" },
  { value: "fr", label: "Francais" },
  { value: "de", label: "Deutsch" },
  { value: "pt", label: "Portugues" },
  { value: "it", label: "Italiano" },
];

export function Sidebar({ config, onChange, isOpen, onClose }: SidebarProps) {
  const update = (partial: Partial<AppConfig>) =>
    onChange({ ...config, ...partial });

  return (
    <>
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/30 z-40 lg:hidden"
          onClick={onClose}
        />
      )}

      <aside
        className={`fixed top-0 right-0 h-full w-80 bg-white shadow-xl z-50 transform transition-transform duration-300 ${
          isOpen ? "translate-x-0" : "translate-x-full"
        }`}
      >
        <div className="p-5">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-sm font-semibold uppercase tracking-wider text-text-primary">
              Configuracion
            </h2>
            <button
              onClick={onClose}
              className="p-1.5 rounded-md hover:bg-gray-100 transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          <div className="space-y-5">
            {/* Whisper Provider */}
            <div>
              <label className="block text-xs font-medium text-text-muted mb-1.5">
                Transcripcion (Whisper)
              </label>
              <select
                value={config.whisperProvider}
                onChange={(e) => update({ whisperProvider: e.target.value })}
                className="w-full px-3 py-2 text-sm border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-accent/30"
              >
                <option value="groq">Groq — Whisper Large v3</option>
                <option value="azure">Azure Whisper (experimental)</option>
              </select>
            </div>

            {/* LLM Provider */}
            <div>
              <label className="block text-xs font-medium text-text-muted mb-1.5">
                Modelo de evaluacion (LLM)
              </label>
              <select
                value={config.llmProvider}
                onChange={(e) => update({ llmProvider: e.target.value })}
                className="w-full px-3 py-2 text-sm border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-accent/30"
              >
                <option value="mistral">Mistral Large — Principal</option>
                <option value="gemini">Gemini 2.0 Flash — Backup</option>
                <option value="azure_openai">Azure OpenAI (experimental)</option>
              </select>
            </div>

            <hr className="border-border" />

            {/* Processing Options */}
            <div>
              <label className="block text-xs font-medium text-text-muted mb-2">
                Procesamiento
              </label>

              <label className="flex items-center gap-2 mb-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={config.cleanTranscription}
                  onChange={(e) =>
                    update({ cleanTranscription: e.target.checked })
                  }
                  className="rounded border-border text-accent focus:ring-accent/30"
                />
                <span className="text-sm">Limpiar transcripcion</span>
              </label>

              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={config.detectReading}
                  onChange={(e) =>
                    update({ detectReading: e.target.checked })
                  }
                  className="rounded border-border text-accent focus:ring-accent/30"
                />
                <span className="text-sm">Detectar lectura / audio IA</span>
              </label>
            </div>

            {/* Language */}
            <div>
              <label className="block text-xs font-medium text-text-muted mb-1.5">
                Idioma del audio
              </label>
              <select
                value={config.language}
                onChange={(e) => update({ language: e.target.value })}
                className="w-full px-3 py-2 text-sm border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-accent/30"
              >
                {LANGUAGES.map((l) => (
                  <option key={l.value} value={l.value}>
                    {l.label}
                  </option>
                ))}
              </select>
            </div>

            <hr className="border-border" />

            {/* API Keys */}
            <div>
              <div className="flex items-center gap-1.5 mb-3">
                <KeyRound className="w-3.5 h-3.5 text-text-muted" />
                <label className="text-xs font-medium text-text-muted">
                  Claves de API
                </label>
              </div>
              <p className="text-xs text-text-muted mb-3">
                Opcional si ya estan en el servidor (.env)
              </p>

              <div className="space-y-2">
                <div>
                  <div className="flex items-center gap-1 mb-1">
                    {config.groqApiKey
                      ? <CheckCircle className="w-3 h-3 text-emerald-500" />
                      : <AlertCircle className="w-3 h-3 text-amber-400" />}
                    <span className="text-xs text-text-muted">Groq API Key</span>
                  </div>
                  <input
                    type="password"
                    value={config.groqApiKey}
                    onChange={(e) => update({ groqApiKey: e.target.value })}
                    placeholder="gsk_..."
                    className="w-full px-2 py-1.5 text-xs border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-accent/30 font-mono"
                  />
                </div>

                {config.llmProvider === "mistral" && (
                  <div>
                    <div className="flex items-center gap-1 mb-1">
                      {config.mistralApiKey
                        ? <CheckCircle className="w-3 h-3 text-emerald-500" />
                        : <AlertCircle className="w-3 h-3 text-amber-400" />}
                      <span className="text-xs text-text-muted">Mistral API Key</span>
                    </div>
                    <input
                      type="password"
                      value={config.mistralApiKey}
                      onChange={(e) => update({ mistralApiKey: e.target.value })}
                      placeholder="..."
                      className="w-full px-2 py-1.5 text-xs border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-accent/30 font-mono"
                    />
                  </div>
                )}

                {config.llmProvider === "gemini" && (
                  <div>
                    <div className="flex items-center gap-1 mb-1">
                      {config.googleApiKey
                        ? <CheckCircle className="w-3 h-3 text-emerald-500" />
                        : <AlertCircle className="w-3 h-3 text-amber-400" />}
                      <span className="text-xs text-text-muted">Google API Key</span>
                    </div>
                    <input
                      type="password"
                      value={config.googleApiKey}
                      onChange={(e) => update({ googleApiKey: e.target.value })}
                      placeholder="AIza..."
                      className="w-full px-2 py-1.5 text-xs border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-accent/30 font-mono"
                    />
                  </div>
                )}

                {(config.llmProvider === "azure_openai" || config.whisperProvider === "azure") && (
                  <div className="space-y-2">
                    <div>
                      <div className="flex items-center gap-1 mb-1">
                        {config.azureApiKey
                          ? <CheckCircle className="w-3 h-3 text-emerald-500" />
                          : <AlertCircle className="w-3 h-3 text-amber-400" />}
                        <span className="text-xs text-text-muted">Azure OpenAI Key</span>
                      </div>
                      <input
                        type="password"
                        value={config.azureApiKey}
                        onChange={(e) => update({ azureApiKey: e.target.value })}
                        placeholder="..."
                        className="w-full px-2 py-1.5 text-xs border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-accent/30 font-mono"
                      />
                    </div>
                    <div>
                      <span className="text-xs text-text-muted block mb-1">Azure Endpoint</span>
                      <input
                        type="text"
                        value={config.azureEndpoint}
                        onChange={(e) => update({ azureEndpoint: e.target.value })}
                        placeholder="https://tu-recurso.openai.azure.com"
                        className="w-full px-2 py-1.5 text-xs border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-accent/30 font-mono"
                      />
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
}
