"use client"

import { useEffect, useState, useMemo } from "react"
import { cn } from "@/lib/utils"

interface LoadingScreenProps {
  onLoadingComplete: () => void
  minimumDuration?: number
}

// Full screen grid - calculate based on viewport
const GRID_COLS = 12
const GRID_ROWS = 8

export function LoadingScreen({ onLoadingComplete, minimumDuration = 3500 }: LoadingScreenProps) {
  const [progress, setProgress] = useState(0)
  const [currentStep, setCurrentStep] = useState(0)
  const [isExiting, setIsExiting] = useState(false)
  const [revealedTiles, setRevealedTiles] = useState<Set<number>>(new Set())
  const [flashingTiles, setFlashingTiles] = useState<Set<number>>(new Set())

  const loadingSteps = [
    "Initializing mapping system...",
    "Loading satellite imagery...",
    "Processing grid sectors...",
    "Calibrating coordinates...",
    "System ready"
  ]

  // Generate random road patterns for each tile
  const tilePatterns = useMemo(() => {
    const patterns: string[][] = []
    for (let i = 0; i < GRID_COLS * GRID_ROWS; i++) {
      const paths: string[] = []
      const numPaths = Math.floor(Math.random() * 5) + 2
      
      for (let j = 0; j < numPaths; j++) {
        const pathType = Math.floor(Math.random() * 6)
        switch (pathType) {
          case 0:
            paths.push(`M0,${20 + Math.random() * 60} L100,${20 + Math.random() * 60}`)
            break
          case 1:
            paths.push(`M${20 + Math.random() * 60},0 L${20 + Math.random() * 60},100`)
            break
          case 2:
            paths.push(`M0,${Math.random() * 50} L100,${50 + Math.random() * 50}`)
            break
          case 3:
            paths.push(`M0,${50 + Math.random() * 30} Q${50},${Math.random() * 100} 100,${50 + Math.random() * 30}`)
            break
          case 4:
            paths.push(`M${30 + Math.random() * 40},0 L${30 + Math.random() * 40},100`)
            paths.push(`M0,${30 + Math.random() * 40} L100,${30 + Math.random() * 40}`)
            break
          case 5:
            paths.push(`M50,100 L50,50 L${Math.random() > 0.5 ? 0 : 100},0`)
            break
        }
      }
      patterns.push(paths)
    }
    return patterns
  }, [])

  // Randomize tile reveal order
  const revealOrder = useMemo(() => {
    const indices = Array.from({ length: GRID_COLS * GRID_ROWS }, (_, i) => i)
    for (let i = indices.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1))
      ;[indices[i], indices[j]] = [indices[j], indices[i]]
    }
    return indices
  }, [])

  // Pre-calculate tile brightness for consistency
  const tileBrightness = useMemo(() => {
    return Array.from({ length: GRID_COLS * GRID_ROWS }, () => 0.4 + Math.random() * 0.4)
  }, [])

  useEffect(() => {
    const stepDuration = minimumDuration / loadingSteps.length
    const totalTiles = GRID_COLS * GRID_ROWS
    const tileRevealInterval = (minimumDuration * 0.85) / totalTiles

    const progressInterval = setInterval(() => {
      setProgress(prev => {
        const next = prev + 1
        if (next >= 100) {
          clearInterval(progressInterval)
          return 100
        }
        return next
      })
    }, minimumDuration / 100)

    const stepInterval = setInterval(() => {
      setCurrentStep(prev => {
        if (prev >= loadingSteps.length - 1) {
          clearInterval(stepInterval)
          return prev
        }
        return prev + 1
      })
    }, stepDuration)

    let tileIndex = 0
    const tileInterval = setInterval(() => {
      if (tileIndex < totalTiles) {
        const tileToReveal = revealOrder[tileIndex]
        
        setFlashingTiles(prev => new Set([...prev, tileToReveal]))
        
        setTimeout(() => {
          setFlashingTiles(prev => {
            const newSet = new Set(prev)
            newSet.delete(tileToReveal)
            return newSet
          })
          setRevealedTiles(prev => new Set([...prev, tileToReveal]))
        }, 120)
        
        tileIndex++
      } else {
        clearInterval(tileInterval)
      }
    }, tileRevealInterval)

    const exitTimer = setTimeout(() => {
      setIsExiting(true)
      setTimeout(onLoadingComplete, 500)
    }, minimumDuration)

    return () => {
      clearInterval(progressInterval)
      clearInterval(stepInterval)
      clearInterval(tileInterval)
      clearTimeout(exitTimer)
    }
  }, [minimumDuration, onLoadingComplete, loadingSteps.length, revealOrder])

  return (
    <div
      className={cn(
        "fixed inset-0 z-50 flex flex-col items-center justify-center bg-black transition-opacity duration-500 overflow-hidden",
        isExiting && "opacity-0 pointer-events-none"
      )}
    >
      {/* Background city map image */}
      <div 
        className="absolute inset-0 bg-cover bg-center opacity-60"
        style={{
          backgroundImage: `url('https://hebbkx1anhila5yf.public.blob.vercel-storage.com/Screenshot%202026-03-10%20085514-8LJjsPY2r4i0UtJLhYudocZVcW1crt.png')`,
          filter: 'grayscale(100%) contrast(1.2)'
        }}
      />

      {/* Dark overlay for better contrast */}
      <div className="absolute inset-0 bg-black/40" />

      {/* Title */}
      <div className="absolute top-8 text-center z-20">
        <h1 className="text-2xl font-light tracking-[0.4em] text-white uppercase">
          Mapping
        </h1>
        <p className="text-xs text-white/60 tracking-[0.2em] mt-1">
          Road Detection System
        </p>
      </div>

      {/* Compass directions */}
      <div className="absolute top-20 left-1/2 -translate-x-1/2 text-sm font-medium text-white/80 z-20">
        N
      </div>
      <div className="absolute bottom-28 left-1/2 -translate-x-1/2 text-sm font-medium text-white/80 z-20">
        S
      </div>
      <div className="absolute top-1/2 left-8 -translate-y-1/2 text-sm font-medium text-white/80 z-20">
        W
      </div>
      <div className="absolute top-1/2 right-8 -translate-y-1/2 text-sm font-medium text-white/80 z-20">
        E
      </div>

      {/* Full screen grid overlay */}
      <div 
        className="absolute inset-0 z-10"
        style={{
          display: 'grid',
          gridTemplateColumns: `repeat(${GRID_COLS}, 1fr)`,
          gridTemplateRows: `repeat(${GRID_ROWS}, 1fr)`,
        }}
      >
        {Array.from({ length: GRID_COLS * GRID_ROWS }).map((_, index) => {
          const isRevealed = revealedTiles.has(index)
          const isFlashing = flashingTiles.has(index)
          
          return (
            <div
              key={index}
              className={cn(
                "relative border border-white/10 transition-all duration-300",
                !isRevealed && !isFlashing && "bg-black/70"
              )}
            >
              {/* Block overlay - covers the map until revealed */}
              <div 
                className={cn(
                  "absolute inset-0 transition-all duration-300",
                  isFlashing && "bg-white/90",
                  !isRevealed && !isFlashing && "bg-black/80",
                  isRevealed && !isFlashing && "bg-transparent"
                )}
                style={{
                  opacity: isFlashing ? 1 : isRevealed ? 0.15 * tileBrightness[index] : 0.85
                }}
              />

              {/* Road pattern SVG overlay */}
              <svg 
                viewBox="0 0 100 100" 
                className={cn(
                  "absolute inset-0 w-full h-full transition-opacity duration-500",
                  isRevealed ? "opacity-30" : "opacity-0"
                )}
                preserveAspectRatio="none"
              >
                {tilePatterns[index].map((path, pathIndex) => (
                  <path
                    key={pathIndex}
                    d={path}
                    fill="none"
                    stroke="rgba(255,255,255,0.4)"
                    strokeWidth="0.8"
                    strokeLinecap="round"
                  />
                ))}
              </svg>
            </div>
          )
        })}
      </div>

      {/* Scanning line effect */}
      <div 
        className="absolute left-0 right-0 h-[2px] z-20 pointer-events-none"
        style={{
          top: `${(progress / 100) * 100}%`,
          background: 'linear-gradient(90deg, transparent 0%, rgba(96, 165, 250, 0.8) 50%, transparent 100%)',
          boxShadow: '0 0 20px rgba(96, 165, 250, 0.6), 0 0 40px rgba(96, 165, 250, 0.3)'
        }}
      />

      {/* Scale markers at bottom */}
      <div className="absolute bottom-24 left-8 right-8 flex justify-between text-xs text-white/50 font-mono z-20">
        <span>0</span>
        <span>300</span>
        <span>600</span>
        <span>900</span>
        <span>1500</span>
        <span>2100</span>
        <span>M</span>
      </div>

      {/* Bottom info panel - distinct glass morphism card */}
      <div className="absolute bottom-8 left-1/2 -translate-x-1/2 z-30">
        <div className="relative px-10 py-6 rounded-xl border border-white/20 bg-black/80 backdrop-blur-xl shadow-2xl shadow-black/50">
          {/* Glow effect */}
          <div className="absolute inset-0 rounded-xl bg-gradient-to-b from-blue-500/10 to-transparent pointer-events-none" />
          <div className="absolute -inset-[1px] rounded-xl bg-gradient-to-b from-white/10 to-transparent pointer-events-none" />
          
          <div className="relative flex flex-col items-center gap-4">
            {/* Status header */}
            <div className="flex items-center gap-3">
              <div className="relative">
                <div className="w-3 h-3 rounded-full bg-blue-500" />
                <div className="absolute inset-0 w-3 h-3 rounded-full bg-blue-500 animate-ping opacity-75" />
              </div>
              <p className="text-sm text-white font-medium tracking-wide">
                {loadingSteps[currentStep]}
              </p>
            </div>

            {/* Progress bar */}
            <div className="w-72 space-y-3">
              <div className="h-2 bg-white/5 rounded-full overflow-hidden border border-white/10">
                <div 
                  className="h-full bg-gradient-to-r from-blue-600 via-blue-500 to-cyan-400 transition-all duration-100 ease-out rounded-full relative"
                  style={{ width: `${progress}%` }}
                >
                  <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/40 to-transparent animate-shimmer" />
                  <div className="absolute right-0 top-0 bottom-0 w-4 bg-white/30 blur-sm" />
                </div>
              </div>
              <div className="flex justify-between text-xs font-mono">
                <span className="text-white/70">Sectors: <span className="text-blue-400">{revealedTiles.size}</span>/{GRID_COLS * GRID_ROWS}</span>
                <span className="text-white font-semibold">{progress}%</span>
              </div>
            </div>

            {/* Coordinate display */}
            <div className="flex gap-8 pt-2 border-t border-white/10 w-full justify-center">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-emerald-500 shadow-lg shadow-emerald-500/50" />
                <span className="text-xs font-mono text-white/60">LAT: <span className="text-emerald-400">{(30.2672 + Math.sin(progress * 0.1) * 0.01).toFixed(4)}</span></span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-red-500 shadow-lg shadow-red-500/50" />
                <span className="text-xs font-mono text-white/60">LON: <span className="text-red-400">{(-97.7431 + Math.cos(progress * 0.1) * 0.01).toFixed(4)}</span></span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <style jsx>{`
        @keyframes shimmer {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(100%); }
        }
        .animate-shimmer {
          animation: shimmer 1.5s infinite;
        }
      `}</style>
    </div>
  )
}
