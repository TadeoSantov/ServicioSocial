import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Evaluador de Examenes Orales",
  description: "Sistema de evaluacion automatizada con IA",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="es">
      <body className="min-h-screen bg-surface-alt">
        {children}
      </body>
    </html>
  );
}
