'use client'

import {
  useRef,
  useEffect,
  useCallback,
  forwardRef,
  useImperativeHandle,
} from 'react'

interface Point {
  x: number
  y: number
}

interface MapCanvasProps {
  imageData: string | null
  roadMaskData: string | null
  startPoint: Point | null
  goalPoint: Point | null
  path: number[][] | null
  overlayOpacity: number
  showOverlay: boolean
  onCanvasClick: (x: number, y: number) => void
  isLoading: boolean
}

export interface MapCanvasRef {
  getImageDimensions: () => { width: number; height: number }
}

const MapCanvas = forwardRef<MapCanvasRef, MapCanvasProps>(
  (
    {
      imageData,
      roadMaskData,
      startPoint,
      goalPoint,
      path,
      overlayOpacity,
      showOverlay,
      onCanvasClick,
      isLoading,
    },
    ref
  ) => {
    const containerRef = useRef<HTMLDivElement>(null)
    const baseCanvasRef = useRef<HTMLCanvasElement>(null)
    const overlayCanvasRef = useRef<HTMLCanvasElement>(null)
    const pathCanvasRef = useRef<HTMLCanvasElement>(null)
    const markerCanvasRef = useRef<HTMLCanvasElement>(null)
    const dimensionsRef = useRef({ width: 800, height: 600 })

    useImperativeHandle(ref, () => ({
      getImageDimensions: () => dimensionsRef.current,
    }))

    // Draw base satellite image
    useEffect(() => {
      if (!imageData || !baseCanvasRef.current) return

      const canvas = baseCanvasRef.current
      const ctx = canvas.getContext('2d')
      if (!ctx) return

      const img = new Image()
      img.crossOrigin = 'anonymous'
      img.onload = () => {
        dimensionsRef.current = { width: img.width, height: img.height }

        // Set canvas sizes
        const canvases = [
          baseCanvasRef.current,
          overlayCanvasRef.current,
          pathCanvasRef.current,
          markerCanvasRef.current,
        ]
        canvases.forEach((c) => {
          if (c) {
            c.width = img.width
            c.height = img.height
          }
        })

        ctx.drawImage(img, 0, 0)
      }
      img.src = `data:image/png;base64,${imageData}`
    }, [imageData])

    // Draw road mask overlay
    useEffect(() => {
      if (!overlayCanvasRef.current) return

      const canvas = overlayCanvasRef.current
      const ctx = canvas.getContext('2d')
      if (!ctx) return

      ctx.clearRect(0, 0, canvas.width, canvas.height)

      if (!roadMaskData || !showOverlay) return

      const img = new Image()
      img.crossOrigin = 'anonymous'
      img.onload = () => {
        ctx.globalAlpha = overlayOpacity
        ctx.drawImage(img, 0, 0)
        ctx.globalAlpha = 1
      }
      img.src = `data:image/png;base64,${roadMaskData}`
    }, [roadMaskData, overlayOpacity, showOverlay])

    // Draw path
    useEffect(() => {
      if (!pathCanvasRef.current) return

      const canvas = pathCanvasRef.current
      const ctx = canvas.getContext('2d')
      if (!ctx) return

      ctx.clearRect(0, 0, canvas.width, canvas.height)

      if (!path || path.length < 2) return

      ctx.beginPath()
      ctx.moveTo(path[0][0], path[0][1])

      for (let i = 1; i < path.length; i++) {
        ctx.lineTo(path[i][0], path[i][1])
      }

      ctx.strokeStyle = '#4a9eff'
      ctx.lineWidth = 4
      ctx.lineCap = 'round'
      ctx.lineJoin = 'round'
      ctx.stroke()

      // Add glow effect
      ctx.strokeStyle = 'rgba(74, 158, 255, 0.3)'
      ctx.lineWidth = 10
      ctx.stroke()
    }, [path])

    // Draw markers
    useEffect(() => {
      if (!markerCanvasRef.current) return

      const canvas = markerCanvasRef.current
      const ctx = canvas.getContext('2d')
      if (!ctx) return

      ctx.clearRect(0, 0, canvas.width, canvas.height)

      const drawMarker = (
        x: number,
        y: number,
        color: string,
        label: string
      ) => {
        const radius = 16

        // Draw outer glow
        ctx.beginPath()
        ctx.arc(x, y, radius + 4, 0, 2 * Math.PI)
        ctx.fillStyle = `${color}40`
        ctx.fill()

        // Draw main circle
        ctx.beginPath()
        ctx.arc(x, y, radius, 0, 2 * Math.PI)
        ctx.fillStyle = color
        ctx.fill()
        ctx.strokeStyle = 'white'
        ctx.lineWidth = 3
        ctx.stroke()

        // Draw label
        ctx.fillStyle = 'white'
        ctx.font = 'bold 14px sans-serif'
        ctx.textAlign = 'center'
        ctx.textBaseline = 'middle'
        ctx.fillText(label, x, y)
      }

      if (startPoint) {
        drawMarker(startPoint.x, startPoint.y, '#22c55e', 'S')
      }

      if (goalPoint) {
        drawMarker(goalPoint.x, goalPoint.y, '#ef4444', 'G')
      }
    }, [startPoint, goalPoint])

    // Handle click
    const handleClick = useCallback(
      (event: React.MouseEvent<HTMLCanvasElement>) => {
        if (isLoading) return

        const canvas = markerCanvasRef.current
        if (!canvas) return

        const rect = canvas.getBoundingClientRect()
        const scaleX = canvas.width / rect.width
        const scaleY = canvas.height / rect.height

        const x = Math.floor((event.clientX - rect.left) * scaleX)
        const y = Math.floor((event.clientY - rect.top) * scaleY)

        onCanvasClick(x, y)
      },
      [onCanvasClick, isLoading]
    )

    return (
      <div
        ref={containerRef}
        className="relative w-full overflow-hidden rounded-lg border-2 border-border bg-secondary"
        style={{ height: 'calc(100vh - 280px)', minHeight: '400px' }}
      >
        {!imageData && (
          <div className="flex h-full items-center justify-center text-muted-foreground">
            <p>Upload a satellite image to get started</p>
          </div>
        )}
        <div
          className="relative h-full w-full flex items-center justify-center overflow-auto"
          style={{
            display: imageData ? 'flex' : 'none',
          }}
        >
          <div className="relative inline-block">
            <canvas
              ref={baseCanvasRef}
              className="block max-h-full max-w-full"
              style={{ imageRendering: 'auto', objectFit: 'contain' }}
            />
            <canvas
              ref={overlayCanvasRef}
              className="pointer-events-none absolute left-0 top-0 block max-h-full max-w-full"
              style={{ imageRendering: 'auto', objectFit: 'contain' }}
            />
            <canvas
              ref={pathCanvasRef}
              className="pointer-events-none absolute left-0 top-0 block max-h-full max-w-full"
              style={{ imageRendering: 'auto', objectFit: 'contain' }}
            />
            <canvas
              ref={markerCanvasRef}
              className="absolute left-0 top-0 block max-h-full max-w-full cursor-crosshair"
              style={{ imageRendering: 'auto', objectFit: 'contain' }}
              onClick={handleClick}
            />
          </div>
          {isLoading && (
            <div className="absolute inset-0 flex items-center justify-center bg-background/50">
              <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
            </div>
          )}
        </div>
      </div>
    )
  }
)

MapCanvas.displayName = 'MapCanvas'

export default MapCanvas
