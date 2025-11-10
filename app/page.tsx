"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Clock } from "lucide-react"

export default function Home() {
  const [isStarted, setIsStarted] = useState(false)

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="border-b border-border py-4 px-8">
        <div className="flex justify-between items-center max-w-7xl mx-auto">
          <h1 className="text-sm font-medium">DS3 Fall Projects</h1>
          <nav className="flex gap-8 text-sm text-muted-foreground">
            <span>Jaden Lee</span>
            <span>Kylan Huynh</span>
            <span>Yash Date</span>
            <span>Max Ha</span>
          </nav>
        </div>
      </header>

      <div className="flex">
        {/* Left Sidebar */}
        <aside className="w-[500px] border-r border-border p-8 min-h-screen">
          <div className="space-y-6">
            <h1 className="text-5xl font-bold">sayStroop</h1>

            <div>
              <h2 className="text-red-500 font-semibold text-lg mb-2">Welcome! Ready to Test Your Brain?</h2>
              <p className="text-sm text-muted-foreground leading-relaxed">
                Our project this quarter explored the Stroop Effect, a fascinating study on attention and reaction time.
                This website lets you take the Stroop test and help us discover whether the effect really works!
              </p>
            </div>

            <Button onClick={() => setIsStarted(true)} className="w-fit bg-black text-white hover:bg-black/90">
              Take the Test Below
            </Button>

            <div className="space-y-4">
              <div className="flex items-center gap-2">
                <Clock className="w-4 h-4" />
                <span className="font-medium">Stroop Test</span>
              </div>

              <div className="bg-red-500 p-8 rounded-lg text-center">
                <h3 className="text-white text-3xl font-bold leading-tight">
                  Display Random Word In Corresponding color
                </h3>
              </div>

              <Button onClick={() => setIsStarted(true)} className="bg-green-600 hover:bg-green-700 text-white w-32">
                START
              </Button>
            </div>
          </div>
        </aside>

        {/* Main Test Area */}
        <main className="flex-1 bg-black">
          {isStarted ? (
            <StroopTest />
          ) : (
            <div className="h-full flex items-center justify-center text-gray-500">
              <p className="text-xl">Click START to begin the test</p>
            </div>
          )}
        </main>
      </div>
    </div>
  )
}

function StroopTest() {
  const [currentTrial, setCurrentTrial] = useState(1)
  const [timeLeft, setTimeLeft] = useState(30)
  const [results, setResults] = useState<Array<{ trial: number; correct: boolean; time: number }>>([])

  const colors = ["red", "blue", "green", "yellow", "purple", "orange"]
  const colorMap = {
    red: "#ef4444",
    blue: "#3b82f6",
    green: "#22c55e",
    yellow: "#eab308",
    purple: "#a855f7",
    orange: "#f97316",
  }

  // Generate random word and color (intentionally mismatched for Stroop effect)
  const [currentWord, setCurrentWord] = useState(() => colors[Math.floor(Math.random() * colors.length)])
  const [currentColor, setCurrentColor] = useState(() => {
    const availableColors = colors.filter((c) => c !== currentWord)
    return availableColors[Math.floor(Math.random() * availableColors.length)]
  })

  const handleAnswer = (answer: string) => {
    const correct = answer === currentColor
    setResults([...results, { trial: currentTrial, correct, time: 30 - timeLeft }])

    if (currentTrial < 10) {
      // Generate next trial
      const newWord = colors[Math.floor(Math.random() * colors.length)]
      const availableColors = colors.filter((c) => c !== newWord)
      const newColor = availableColors[Math.floor(Math.random() * availableColors.length)]

      setCurrentWord(newWord)
      setCurrentColor(newColor)
      setCurrentTrial(currentTrial + 1)
      setTimeLeft(30)
    } else {
      // Test complete
      alert(`Test Complete! You got ${results.filter((r) => r.correct).length} out of 10 correct!`)
    }
  }

  return (
    <div className="h-full flex flex-col">
      {/* Timer and Progress */}
      <div className="p-8 flex justify-end items-center gap-4 text-white">
        <Clock className="w-5 h-5" />
        <div className="text-right">
          <div className="text-3xl font-bold">
            {Math.floor(timeLeft / 60)}:{(timeLeft % 60).toString().padStart(2, "0")}
          </div>
          <div className="text-sm text-gray-400">{currentTrial}/10</div>
        </div>
      </div>

      {/* Test Slide */}
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center space-y-8">
          <div
            className="text-9xl font-bold uppercase tracking-tight"
            style={{ color: colorMap[currentColor as keyof typeof colorMap] }}
          >
            {currentWord}
          </div>
          <div className="text-sm text-gray-400 lowercase">{currentColor}</div>
        </div>
      </div>

      {/* Answer Buttons */}
      <div className="p-8 flex flex-wrap gap-3 justify-center">
        {colors.map((color) => (
          <Button
            key={color}
            onClick={() => handleAnswer(color)}
            className="capitalize text-lg px-6 py-3"
            style={{
              backgroundColor: colorMap[color as keyof typeof colorMap],
              color: "white",
            }}
          >
            {color}
          </Button>
        ))}
      </div>

      {/* Test Slide Label */}
      <div className="text-center pb-8 text-gray-500 text-sm">Test Slide</div>
    </div>
  )
}
