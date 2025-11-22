import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'RealThon 2025',
  description: 'RealThon 2025 Project',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ko">
      <body>{children}</body>
    </html>
  )
}
