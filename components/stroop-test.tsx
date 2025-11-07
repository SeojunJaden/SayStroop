"use client"

import { useState, useEffect, useCallback } from "react"
import { Button } from "@/components/ui/button"

interface StroopTestProps {
  onComplete: () => void
}

const COLORS = ["RED", "BLUE", "GREEN", "YELLOW", "PURPLE", "ORANGE"]
const COLOR_MAP: Record<string, string> = {
  RED: "#EF4444",
  BLUE: "#3B82F6",
  GREEN: "#22C55E",
  YELLOW: "#EAB308",
  PURPLE: "#A855F7",
  ORANGE: "#F97316",
}

const TOTAL_QUESTIONS = 10

export function StroopTest({ onComplete }: StroopTestProps) {
  const [currentQuestion, setCurrentQuestion] = useState(1)
  const [word, setWord] = useState("")
  const [color, setColor] = useState("")
  const [startTime, setStartTime] = useState(Date.now())
  const [elapsedTime, setElapsedTime] = useState(0)
  const [responses, setResponses] = useState<Array<{ word: string; color: string; time: number; correct: boolean }>>([])
  const [showResults, setShowResults] = useState(false)

  // Generate random word and color (ensuring they're different for the Stroop effect)
  const generateQuestion = useCallback(() => {
    const randomWord = COLORS[Math.floor(Math.random() * COLORS.length)]
    let randomColor = COLORS[Math.floor(Math.random() * COLORS.length)]

    // Ensure color is different from word for true Stroop effect
    while (randomColor === randomWord) {
      randomColor = COLORS[Math.floor(Math.random() * COLORS.length)]
    }

    setWord(randomWord)
    setColor(randomColor)
    setStartTime(Date.now())
  }, [])

  useEffect(() => {
    generateQuestion()
  }, [generateQuestion])

  // Timer
  useEffect(() => {
    const interval = setInterval(() => {
      setElapsedTime(Math.floor((Date.now() - startTime) / 1000))
    }, 100)

    return () => clearInterval(interval)
  }, [startTime])

  const handleColorClick = (selectedColor: string) => {
    const responseTime = Date.now() - startTime
    const correct = selectedColor === color

    setResponses([...responses, { word, color, time: responseTime, correct }])

    if (currentQuestion < TOTAL_QUESTIONS) {
      setCurrentQuestion(currentQuestion + 1)
      generateQuestion()
    } else {
      setShowResults(true)
    }
  }

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, "0")}`
  }

  if (showResults) {
    const correctCount = responses.filter((r) => r.correct).length
    const avgTime = responses.reduce((sum, r) => sum + r.time, 0) / responses.length

    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-900">
        <div className="w-full max-w-2xl rounded-lg bg-white p-12 text-center">
          <h2 className="mb-6 text-4xl font-bold">Test Complete!</h2>
          <div className="mb-8 space-y-4">
            <p className="text-2xl">
              Score:{" "}
              <span className="font-bold">
                {correctCount}/{TOTAL_QUESTIONS}
              </span>
            </p>
            <p className="text-xl text-gray-600">Average Response Time: {(avgTime / 1000).toFixed(2)}s</p>
          </div>
          <Button onClick={onComplete} className="bg-black px-8 py-3 text-white hover:bg-gray-800">
            Back to Home
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-gray-900 text-white">
      {/* Timer and Progress */}
      <div className="absolute right-8 top-8 text-right">
        <div className="mb-2 flex items-center justify-end gap-2">
          <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <circle cx="12" cy="12" r="10" strokeWidth="2" />
            <path strokeWidth="2" d="M12 6v6l4 2" />
          </svg>
          <span className="text-3xl font-bold">{formatTime(elapsedTime)}</span>
        </div>
        <p className="text-lg text-gray-400">
          {currentQuestion}/{TOTAL_QUESTIONS}
        </p>
      </div>

      {/* Main Test Area */}
      <div className="text-center">
        <p className="mb-8 text-xl text-gray-400">Test Slide</p>

        <div className="mb-16">
          <h1 className="mb-4 text-8xl font-bold" style={{ color: COLOR_MAP[color] }}>
            {word}
          </h1>
          <p className="text-sm text-gray-500">Click the color you see (not the word)</p>
        </div>

        {/* Color Selection Buttons */}
        <div className="flex flex-wrap justify-center gap-4">
          {COLORS.map((colorName) => (
            <Button
              key={colorName}
              onClick={() => handleColorClick(colorName)}
              className="min-w-[120px] px-6 py-3 text-lg font-semibold"
              style={{
                backgroundColor: COLOR_MAP[colorName],
                color: "white",
              }}
            >
              {colorName}
            </Button>
          ))}
        </div>
      </div>
    </div>
  )
}
