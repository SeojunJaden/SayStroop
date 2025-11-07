"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { StroopTest } from "@/components/stroop-test"

export default function Home() {
  const [testStarted, setTestStarted] = useState(false)

  if (testStarted) {
    return <StroopTest onComplete={() => setTestStarted(false)} />
  }

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <h1 className="text-sm font-medium">DS3 Fall Projects</h1>
          <div className="flex gap-8 text-sm">
            <span>Jaden Lee</span>
            <span>Kylan Huynh</span>
            <span>Yash Date</span>
            <span>Max Ha</span>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="mx-auto max-w-2xl px-6 py-16">
        <h2 className="mb-6 text-5xl font-bold">sayStroop</h2>

        <div className="mb-8">
          <h3 className="mb-3 text-lg font-semibold text-red-600">Welcome! Ready to Test Your Brain?</h3>
          <p className="leading-relaxed text-gray-700">
            Our project this quarter explored the Stroop Effect, a fascinating study on attention and reaction time.
            This website lets you take the Stroop test and help us discover whether the effect really works!
          </p>
        </div>

        <div className="mb-6 flex items-center gap-3">
          <Button
            onClick={() => setTestStarted(true)}
            className="bg-black px-6 py-2 text-sm font-medium text-white hover:bg-gray-800"
          >
            Take the Test Below
          </Button>
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <circle cx="12" cy="12" r="10" strokeWidth="2" />
              <path strokeWidth="2" d="M12 6v6l4 2" />
            </svg>
          </div>
        </div>

        {/* Test Preview Box */}
        <div className="mb-4 flex items-center gap-2 text-sm">
          <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <circle cx="12" cy="12" r="10" strokeWidth="2" />
            <path strokeWidth="2" d="M12 6v6l4 2" />
          </svg>
          <span className="font-medium">Stroop Test</span>
        </div>

        <div className="rounded-lg bg-red-600 p-12 text-center">
          <h4 className="mb-4 text-3xl font-bold text-white">Display Random Word In Corresponding color</h4>
        </div>

        <Button
          onClick={() => setTestStarted(true)}
          className="mt-4 bg-green-600 px-8 py-2 text-sm font-semibold uppercase text-white hover:bg-green-700"
        >
          Start
        </Button>
      </main>
    </div>
  )
}
