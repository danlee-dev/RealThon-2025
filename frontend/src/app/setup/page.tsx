'use client'

import { useState, useEffect, useRef } from 'react'
import { useRouter } from 'next/navigation'

export default function SetupPage() {
  const router = useRouter()
  const videoRef = useRef<HTMLVideoElement>(null)
  const [stream, setStream] = useState<MediaStream | null>(null)
  const [cameraReady, setCameraReady] = useState(false)
  const [micReady, setMicReady] = useState(false)
  const [speakerReady, setSpeakerReady] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string>('')

  useEffect(() => {
    checkDevices()
    return () => {
      if (stream) {
        stream.getTracks().forEach(track => track.stop())
      }
    }
  }, [])

  const checkDevices = async () => {
    try {
      const devices = await navigator.mediaDevices.enumerateDevices()
      const hasCamera = devices.some(device => device.kind === 'videoinput')
      const hasMic = devices.some(device => device.kind === 'audioinput')
      const hasSpeaker = devices.some(device => device.kind === 'audiooutput')

      setCameraReady(hasCamera)
      setMicReady(hasMic)
      setSpeakerReady(hasSpeaker)
    } catch (err) {
      setError('장치 확인 중 오류가 발생했습니다.')
    }
  }

  const startCamera = async () => {
    setIsLoading(true)
    setError('')
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: { width: 1280, height: 720 },
        audio: true
      })
      setStream(mediaStream)
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream
      }
      setCameraReady(true)
      setMicReady(true)
    } catch (err) {
      setError('카메라 또는 마이크 접근에 실패했습니다. 권한을 확인해주세요.')
      setCameraReady(false)
    } finally {
      setIsLoading(false)
    }
  }

  const testSpeaker = () => {
    const audio = new Audio('/test-sound.mp3')
    audio.play().catch(() => {
      setError('스피커 테스트 실패')
    })
    setSpeakerReady(true)
  }

  const handleStart = () => {
    if (stream) {
      router.push('/interview')
    }
  }

  const allReady = cameraReady && micReady && speakerReady && stream

  return (
    <main className="min-h-screen flex items-center justify-center p-6">
      <div className="w-full max-w-5xl">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-black text-ink mb-3">
            정확한 분석을 위해{' '}
            <span className="bg-brand text-ink px-3 py-1 neon-glow">면접 환경</span>
            을 체크해볼게요!
          </h1>
          <p className="text-ink-light text-lg">모든 장치가 연결되어야 면접을 시작할 수 있어요</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Camera Preview */}
          <div className="space-y-4">
            <div className={`relative aspect-video bg-ink rounded-xl overflow-hidden shadow-2xl ${stream ? 'neon-border' : 'border-4 border-ink'}`}>
              {stream ? (
                <video
                  ref={videoRef}
                  autoPlay
                  playsInline
                  muted
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="text-center">
                    <svg className="w-24 h-24 mx-auto mb-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                    </svg>
                    <p className="text-gray-500 font-bold">카메라 미리보기</p>
                  </div>
                </div>
              )}
            </div>

            {!stream && (
              <button
                onClick={startCamera}
                disabled={isLoading}
                className="w-full py-4 px-4 bg-brand text-ink rounded-xl hover:neon-glow transition-all border-3 border-ink disabled:opacity-50 font-black text-lg uppercase tracking-wide"
              >
                {isLoading ? '연결 중...' : '카메라 및 마이크 연결'}
              </button>
            )}

            {error && (
              <div className="p-4 bg-secondary/10 border-3 border-secondary rounded-xl">
                <p className="text-secondary font-bold text-sm">{error}</p>
              </div>
            )}
          </div>

          {/* Device Check List */}
          <div className="space-y-4">
            <div className="glass-effect rounded-xl p-6">
              <h2 className="text-xl font-black text-ink mb-4 border-b-4 border-brand pb-2 inline-block">
                장치 연결 확인
              </h2>

              <div className="space-y-3 mt-6">
                {/* Camera */}
                <div className="flex items-center justify-between p-4 bg-white rounded-xl border-2 border-ink">
                  <div className="flex items-center gap-3">
                    <svg className="w-6 h-6 text-ink" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                    </svg>
                    <span className="font-black text-ink">카메라 연결</span>
                  </div>
                  {cameraReady && stream ? (
                    <span className="flex items-center gap-1 text-secondary font-black">
                      <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                      </svg>
                      연결됨
                    </span>
                  ) : (
                    <span className="text-gray-400 font-bold">대기중</span>
                  )}
                </div>

                {/* Microphone */}
                <div className="flex items-center justify-between p-4 bg-white rounded-xl border-2 border-ink">
                  <div className="flex items-center gap-3">
                    <svg className="w-6 h-6 text-ink" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                    </svg>
                    <span className="font-black text-ink">마이크 연결</span>
                  </div>
                  {micReady && stream ? (
                    <span className="flex items-center gap-1 text-secondary font-black">
                      <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                      </svg>
                      연결됨
                    </span>
                  ) : (
                    <span className="text-gray-400 font-bold">대기중</span>
                  )}
                </div>

                {/* Speaker */}
                <div className="flex items-center justify-between p-4 bg-white rounded-xl border-2 border-ink">
                  <div className="flex items-center gap-3">
                    <svg className="w-6 h-6 text-ink" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
                    </svg>
                    <span className="font-black text-ink">스피커 연결</span>
                  </div>
                  <button
                    onClick={testSpeaker}
                    className="text-sm text-accent hover:text-accent-dark font-black uppercase"
                  >
                    테스트
                  </button>
                </div>
              </div>
            </div>

            {/* Tips */}
            <div className="bg-accent/10 rounded-xl p-6 border-3 border-accent">
              <h3 className="text-sm font-black text-accent mb-3 uppercase tracking-wider">면접 팁</h3>
              <ul className="space-y-2 text-sm text-ink font-bold">
                <li className="flex items-start gap-2">
                  <span className="text-secondary mt-0.5 font-black">→</span>
                  <span>밝은 조명이 있는 곳에서 촬영하세요</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-secondary mt-0.5 font-black">→</span>
                  <span>얼굴이 화면 중앙에 오도록 조정하세요</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-secondary mt-0.5 font-black">→</span>
                  <span>조용한 환경에서 진행하세요</span>
                </li>
              </ul>
            </div>

            {/* Start Button */}
            <button
              onClick={handleStart}
              disabled={!allReady}
              className="w-full py-5 px-6 bg-secondary text-white rounded-xl hover:bg-secondary-light transition-all border-3 border-ink shadow-2xl disabled:opacity-50 disabled:cursor-not-allowed font-black text-xl uppercase tracking-wide neon-glow"
            >
              {allReady ? '🚀 면접 시작하기' : '모든 장치를 연결해주세요'}
            </button>
          </div>
        </div>
      </div>
    </main>
  )
}
