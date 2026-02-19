"use client";

import { useRef, useState, useCallback } from "react";
import { Upload, Mic, MicOff, Trash2 } from "lucide-react";

interface Props {
  audioFile: File | Blob | null;
  audioName: string;
  audioUrl: string | null;
  onAudioSelected: (file: File | Blob, name: string) => void;
  onClearAudio: () => void;
}

export function AudioSection({
  audioFile,
  audioName,
  audioUrl,
  onAudioSelected,
  onClearAudio,
}: Props) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [activeTab, setActiveTab] = useState<"upload" | "record">("upload");
  const [isRecording, setIsRecording] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      onAudioSelected(file, file.name);
    }
  };

  const startRecording = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      chunksRef.current = [];

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data);
      };

      mediaRecorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: "audio/wav" });
        onAudioSelected(blob, "grabacion.wav");
        stream.getTracks().forEach((t) => t.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (err) {
      console.error("Microphone access denied:", err);
    }
  }, [onAudioSelected]);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  }, [isRecording]);

  return (
    <div className="bg-white rounded-lg border border-border p-4">
      <h3 className="text-xs font-semibold uppercase tracking-wider text-text-primary mb-1">
        Audio del examen
      </h3>
      <p className="text-xs text-text-muted mb-4">
        Sube un archivo o graba directamente
      </p>

      {/* Tabs */}
      <div className="flex gap-1 bg-surface-alt p-0.5 rounded-md mb-4 border border-border">
        <button
          onClick={() => setActiveTab("upload")}
          className={`flex-1 flex items-center justify-center gap-1.5 px-3 py-1.5 text-sm font-medium rounded transition-colors ${
            activeTab === "upload"
              ? "bg-white text-text-primary shadow-sm"
              : "text-text-muted hover:text-text-primary"
          }`}
        >
          <Upload className="w-3.5 h-3.5" />
          Subir archivo
        </button>
        <button
          onClick={() => setActiveTab("record")}
          className={`flex-1 flex items-center justify-center gap-1.5 px-3 py-1.5 text-sm font-medium rounded transition-colors ${
            activeTab === "record"
              ? "bg-white text-text-primary shadow-sm"
              : "text-text-muted hover:text-text-primary"
          }`}
        >
          <Mic className="w-3.5 h-3.5" />
          Grabar audio
        </button>
      </div>

      {/* Upload Tab */}
      {activeTab === "upload" && (
        <div>
          <input
            ref={fileInputRef}
            type="file"
            accept=".mp3,.wav,.m4a,.ogg,.flac,.webm"
            onChange={handleFileChange}
            className="hidden"
          />
          <button
            onClick={() => fileInputRef.current?.click()}
            className="w-full border-2 border-dashed border-border rounded-lg py-8 text-center hover:border-accent/50 hover:bg-accent-light/30 transition-colors"
          >
            <Upload className="w-8 h-8 mx-auto text-text-muted mb-2" />
            <p className="text-sm text-text-muted">
              Clic para seleccionar archivo
            </p>
            <p className="text-xs text-text-muted/60 mt-1">
              MP3, WAV, M4A, OGG, FLAC, WEBM — Max 25 MB
            </p>
          </button>
        </div>
      )}

      {/* Record Tab */}
      {activeTab === "record" && (
        <div className="flex items-center gap-4">
          <button
            onClick={isRecording ? stopRecording : startRecording}
            className={`flex items-center gap-2 px-6 py-3 rounded-lg font-medium text-sm transition-colors ${
              isRecording
                ? "bg-danger text-white hover:bg-red-700"
                : "bg-accent text-white hover:bg-blue-600"
            }`}
          >
            {isRecording ? (
              <>
                <MicOff className="w-4 h-4" />
                Detener grabacion
              </>
            ) : (
              <>
                <Mic className="w-4 h-4" />
                Iniciar grabacion
              </>
            )}
          </button>
          {isRecording && (
            <span className="flex items-center gap-2 text-sm text-danger">
              <span className="w-2 h-2 bg-danger rounded-full animate-pulse" />
              Grabando...
            </span>
          )}
        </div>
      )}

      {/* Audio Preview */}
      {audioFile && audioUrl && (
        <div className="mt-4 p-3 bg-surface-alt rounded-lg border border-border">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-text-primary">
              {audioName}
            </span>
            <div className="flex items-center gap-2">
              <span className="text-xs text-text-muted">
                {(audioFile.size / (1024 * 1024)).toFixed(2)} MB
              </span>
              <button
                onClick={onClearAudio}
                className="p-1 rounded hover:bg-red-50 text-text-muted hover:text-danger transition-colors"
              >
                <Trash2 className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
          <audio controls src={audioUrl} className="w-full h-8" />
        </div>
      )}
    </div>
  );
}
