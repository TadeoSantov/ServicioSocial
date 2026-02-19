import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function getQualityColor(value: string): string {
  const colors: Record<string, string> = {
    excelente: "text-success",
    buena: "text-success",
    bueno: "text-success",
    regular: "text-warning",
    deficiente: "text-danger",
  };
  return colors[value?.toLowerCase()] || "text-text-muted";
}

export function getQualityLabel(value: string): string {
  const labels: Record<string, string> = {
    excelente: "Excelente",
    buena: "Buena",
    bueno: "Bueno",
    regular: "Regular",
    deficiente: "Deficiente",
  };
  return labels[value?.toLowerCase()] || value || "N/A";
}

export function formatDuration(seconds: number): string {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, "0")}`;
}

export function getGradeColor(grade: number): string {
  if (grade >= 9) return "text-success";
  if (grade >= 7) return "text-accent";
  if (grade >= 5) return "text-warning";
  return "text-danger";
}

export function getGradeBg(grade: number): string {
  if (grade >= 9) return "bg-emerald-50 border-emerald-200";
  if (grade >= 7) return "bg-blue-50 border-blue-200";
  if (grade >= 5) return "bg-amber-50 border-amber-200";
  return "bg-red-50 border-red-200";
}
