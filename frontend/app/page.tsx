'use client'

import { useState, useCallback, useRef, useEffect } from 'react'
import { Map, Github } from 'lucide-react'
import { APIClient } from '@/lib/api-client'
import type { Statistics } from '@/lib/api-client'
import MapCanvas, { type MapCanvasRef } from '@/components/map-canvas'
import ControlsPanel from '@/components/controls-panel'
import StatisticsPanel from '@/components/statistics-panel'
import {
  NotificationsContainer,
  useNotifications,
} from '@/components/notifications'
import dynamic from 'next/dynamic'

// Dynamic import for loading screen to avoid hydration issues
const LoadingScreen = dynamic(() => import('@/components/loading-screen').then(mod => ({ default: mod.LoadingScreen })), {
  ssr: false,
  loading: () => (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black">
      <div className="text-white">Loading...</div>
    </div>
  )
})

type SelectionMode = 'idle' | 'selecting-start' | 'selecting-goal'

interface Point {
  x: number
  y: number
}

export default function RoadMappingPage() {
  // Loading screen state
  const [isInitialLoading, setIsInitialLoading] = useState(true)
  const [showLoadingScreen, setShowLoadingScreen] = useState(false)

  // Only show loading screen on client
  useEffect(() => {
    setShowLoadingScreen(true)
  }, [])

  // State
  const [imageId, setImageId] = useState<string | null>(null)
  const [imageData, setImageData] = useState<string | null>(null)
  const [roadMaskData, setRoadMaskData] = useState<string | null>(null)
  const [startPoint, setStartPoint] = useState<Point | null>(null)
  const [goalPoint, setGoalPoint] = useState<Point | null>(null)
  const [path, setPath] = useState<number[][] | null>(null)
  const [statistics, setStatistics] = useState<Statistics | null>(null)
  const [selectionMode, setSelectionMode] =
    useState<SelectionMode>('idle')
  const [showOverlay, setShowOverlay] = useState(true)
  const [overlayOpacity, setOverlayOpacity] = useState(0.5)
  const [isLoading, setIsLoading] = useState(false)

  // Refs
  const mapCanvasRef = useRef<MapCanvasRef>(null)
  const apiClientRef = useRef(new APIClient())

  // Notifications
  const {
    notifications,
    showSuccess,
    showError,
    showInfo,
    showLoading,
    hideLoading,
    dismissNotification,
  } = useNotifications()

  // Handle image upload
  const handleImageUpload = useCallback(
    async (file: File) => {
      setIsLoading(true)
      const loadingId = showLoading('Processing image...')

      try {
        const response = await apiClientRef.current.loadImage(file)

        setImageId(response.image_id)
        setImageData(response.image_data)
        setRoadMaskData(response.road_mask_data)
        setStatistics({
          image_width: response.width,
          image_height: response.height,
          road_coverage_percent: response.road_coverage_percent,
          road_pixels: response.road_pixels,
          total_pixels: response.total_pixels,
          graph_nodes: response.graph_nodes,
          graph_edges: response.graph_edges,
        })
        setStartPoint(null)
        setGoalPoint(null)
        setPath(null)
        setSelectionMode('selecting-start')

        hideLoading(loadingId)
        showSuccess('Image processed successfully')
        showInfo('Click on a road to set the start point')
      } catch (error) {
        hideLoading(loadingId)
        showError(
          error instanceof Error ? error.message : 'Failed to process image'
        )
      } finally {
        setIsLoading(false)
      }
    },
    [showLoading, hideLoading, showSuccess, showError, showInfo]
  )

  // Handle canvas click
  const handleCanvasClick = useCallback(
    async (x: number, y: number) => {
      if (!imageId || isLoading) return

      if (selectionMode === 'selecting-start') {
        setIsLoading(true)
        try {
          const response = await apiClientRef.current.selectStart(imageId, x, y)

          if (response.valid) {
            setStartPoint({ x: response.coordinates.x, y: response.coordinates.y })
            setSelectionMode('selecting-goal')
            showSuccess('Start point selected')
            showInfo('Now click on a road to set the goal point')
          } else {
            showError(response.error || 'Please click on a road')
          }
        } catch (error) {
          showError(
            error instanceof Error ? error.message : 'Failed to select start point'
          )
        } finally {
          setIsLoading(false)
        }
      } else if (selectionMode === 'selecting-goal') {
        setIsLoading(true)
        const loadingId = showLoading('Computing shortest path...')

        try {
          const response = await apiClientRef.current.selectGoal(imageId, x, y)

          if (response.valid) {
            setGoalPoint({ x: response.coordinates.x, y: response.coordinates.y })

            if (response.path) {
              setPath(response.path)
              // Update statistics with path information
              if (response.path_length_pixels && response.path_waypoints) {
                setStatistics(prev => prev ? {
                  ...prev,
                  path_length_pixels: response.path_length_pixels,
                  path_waypoints: response.path_waypoints,
                } : null)
              }
              setSelectionMode('idle')
              hideLoading(loadingId)
              showSuccess('Path computed successfully')
            } else {
              hideLoading(loadingId)
              showInfo('Goal set, but no path found')
              setSelectionMode('idle')
            }
          } else {
            hideLoading(loadingId)
            showError(response.error || 'Please click on a road')
          }
        } catch (error) {
          hideLoading(loadingId)
          showError(
            error instanceof Error ? error.message : 'Failed to select goal point'
          )
        } finally {
          setIsLoading(false)
        }
      } else {
        // Allow re-selecting when in idle mode
        setSelectionMode('selecting-start')
        showInfo('Click on a road to set a new start point')
      }
    },
    [
      imageId,
      isLoading,
      selectionMode,
      showSuccess,
      showError,
      showInfo,
      showLoading,
      hideLoading,
    ]
  )

  // Handle clear selection
  const handleClearSelection = useCallback(async () => {
    if (!imageId) return

    setIsLoading(true)
    try {
      await apiClientRef.current.clearSelection(imageId)
      setStartPoint(null)
      setGoalPoint(null)
      setPath(null)
      // Clear path statistics but keep image statistics
      setStatistics(prev => prev ? {
        ...prev,
        path_length_pixels: undefined,
        path_waypoints: undefined,
      } : null)
      setSelectionMode('selecting-start')
      showSuccess('Selection cleared')
      showInfo('Click on a road to set the start point')
    } catch (error) {
      showError(
        error instanceof Error ? error.message : 'Failed to clear selection'
      )
    } finally {
      setIsLoading(false)
    }
  }, [imageId, showSuccess, showError, showInfo])

  // Show loading screen on initial load
  if (isInitialLoading && showLoadingScreen) {
    return <LoadingScreen onLoadingComplete={() => setIsInitialLoading(false)} />
  }

  // Fallback loading for SSR
  if (isInitialLoading) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-black">
        <div className="text-white">Loading...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Notifications */}
      <NotificationsContainer
        notifications={notifications}
        onDismiss={dismissNotification}
      />

      {/* Header */}
      <header className="border-b border-border bg-card">
        <div className="mx-auto max-w-7xl px-4 py-8">
          <div className="flex flex-col items-center text-center">
            <h1 
              className="text-2xl md:text-3xl lg:text-4xl font-bold text-foreground tracking-tight"
              style={{ 
                fontFamily: 'var(--font-pixel), monospace',
                textShadow: '3px 3px 0px rgba(0,0,0,0.4)',
                letterSpacing: '0.08em',
                lineHeight: '1.4'
              }}
            >
              Road Mapping Interface
            </h1>
            <p className="mt-4 text-sm md:text-base text-muted-foreground tracking-wide">
              Interactive pathfinding on satellite imagery
            </p>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="mx-auto max-w-7xl px-4 py-6">
        <div className="grid gap-6 lg:grid-cols-[1fr_320px]">
          {/* Map Canvas */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-medium text-foreground">Map View</h2>
              {imageData && (
                <span className="text-xs text-muted-foreground">
                  Click on roads to set waypoints
                </span>
              )}
            </div>
            <MapCanvas
              ref={mapCanvasRef}
              imageData={imageData}
              roadMaskData={roadMaskData}
              startPoint={startPoint}
              goalPoint={goalPoint}
              path={path}
              overlayOpacity={overlayOpacity}
              showOverlay={showOverlay}
              onCanvasClick={handleCanvasClick}
              isLoading={isLoading}
            />
          </div>

          {/* Controls and Statistics Panel */}
          <div className="lg:sticky lg:top-6 lg:self-start space-y-6">
            <ControlsPanel
              hasImage={!!imageData}
              hasStartPoint={!!startPoint}
              hasGoalPoint={!!goalPoint}
              hasPath={!!path}
              selectionMode={selectionMode}
              showOverlay={showOverlay}
              overlayOpacity={overlayOpacity}
              isLoading={isLoading}
              onImageUpload={handleImageUpload}
              onClearSelection={handleClearSelection}
              onToggleOverlay={() => setShowOverlay(!showOverlay)}
              onOpacityChange={setOverlayOpacity}
            />
            <StatisticsPanel
              statistics={statistics}
              hasPath={!!path}
            />
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-border bg-card">
        <div className="mx-auto max-w-7xl px-4 py-4">
          <p className="text-center text-xs text-muted-foreground">
            Interactive Road Mapping Interface • Powered by satellite imagery
            analysis
          </p>
        </div>
      </footer>
    </div>
  )
}
