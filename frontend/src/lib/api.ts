import type { HealthResponse, FullPipelineResponse, FullPipelineParams } from "@/types/api";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080";

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const body = await response.text();
    throw new Error(`API error ${response.status}: ${body}`);
  }
  return response.json();
}

export async function checkHealth(): Promise<HealthResponse> {
  const res = await fetch(`${API_BASE}/health`);
  return handleResponse<HealthResponse>(res);
}

export async function runFullPipeline(
  audioFile: File | Blob,
  params: FullPipelineParams
): Promise<FullPipelineResponse> {
  const formData = new FormData();
  formData.append("audio", audioFile);
  formData.append("material", params.material);
  formData.append("rubric", params.rubric);
  formData.append("language", params.language);
  formData.append("whisper_provider", params.whisperProvider);
  formData.append("llm_provider", params.llmProvider);
  formData.append("clean_transcription", String(params.cleanTranscription));
  formData.append("detect_reading", String(params.detectReading));
  if (params.groqApiKey) formData.append("groq_api_key", params.groqApiKey);
  if (params.mistralApiKey) formData.append("mistral_api_key", params.mistralApiKey);
  if (params.googleApiKey) formData.append("google_api_key", params.googleApiKey);
  if (params.azureApiKey) formData.append("azure_api_key", params.azureApiKey);
  if (params.azureEndpoint) formData.append("azure_endpoint", params.azureEndpoint);

  const res = await fetch(`${API_BASE}/api/v1/pipeline`, {
    method: "POST",
    body: formData,
  });

  return handleResponse<FullPipelineResponse>(res);
}
