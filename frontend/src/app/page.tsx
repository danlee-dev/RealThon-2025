'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'

export default function Home() {
  const router = useRouter()

  useEffect(() => {
    router.push('/setup')
  }, [router])

  return (
    <main className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <div className="w-16 h-16 mx-auto mb-4 border-4 border-brand border-t-transparent rounded-full animate-spin"></div>
        <p className="text-gray-600">로딩 중...</p>
      </div>
    </main>
  )
}
