import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'AI 면접 코칭 - 맞춤형 면접 준비 서비스',
  description: '개인 포트폴리오와 직무 정보를 기반으로 AI가 생성하는 맞춤형 면접 질문으로 실전 면접을 준비하세요',
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
