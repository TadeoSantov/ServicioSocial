"use client";

import { Loader2, Play } from "lucide-react";

interface Props {
  isEvaluating: boolean;
  currentStep: string;
  error: string | null;
  onEvaluate: () => void;
}

export function EvaluateButton({
  isEvaluating,
  currentStep,
  error,
  onEvaluate,
}: Props) {
  return (
    <div>
      <button
        onClick={onEvaluate}
        disabled={isEvaluating}
        className="w-full py-3 bg-accent text-white font-medium rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
      >
        {isEvaluating ? (
          <>
            <Loader2 className="w-4 h-4 animate-spin" />
            Evaluando...
          </>
        ) : (
          <>
            <Play className="w-4 h-4" />
            Evaluar examen
          </>
        )}
      </button>

      {isEvaluating && currentStep && (
        <div className="mt-3 p-3 bg-accent-light rounded-lg border border-blue-200">
          <p className="text-sm text-accent font-medium">{currentStep}</p>
        </div>
      )}

      {error && (
        <div className="mt-3 p-3 bg-red-50 rounded-lg border border-red-200">
          <p className="text-sm text-danger font-medium">{error}</p>
        </div>
      )}
    </div>
  );
}
