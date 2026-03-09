'use client'

import { useRef } from 'react'
import { Upload, Trash2, Eye, EyeOff, MapPin, Flag } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Slider } from '@/components/ui/slider'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'

type SelectionMode = 'idle' | 'selecting-start' | 'selecting-goal'

interface ControlsPanelProps {
  hasImage: boolean
  hasStartPoint: boolean
  hasGoalPoint: boolean
  hasPath: boolean
  selectionMode: SelectionMode
  showOverlay: boolean
  overlayOpacity: number
  isLoading: boolean
  onImageUpload: (file: File) => void
  onClearSelection: () => void
  onToggleOverlay: () => void
  onOpacityChange: (value: number) => void
}

export default function ControlsPanel({
  hasImage,
  hasStartPoint,
  hasGoalPoint,
  hasPath,
  selectionMode,
  showOverlay,
  overlayOpacity,
  isLoading,
  onImageUpload,
  onClearSelection,
  onToggleOverlay,
  onOpacityChange,
}: ControlsPanelProps) {
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      onImageUpload(file)
    }
    // Reset input so same file can be selected again
    event.target.value = ''
  }

  const getStatusText = () => {
    if (!hasImage) return 'Upload an image to begin'
    if (selectionMode === 'selecting-start') return 'Click on the map to set start point'
    if (selectionMode === 'selecting-goal') return 'Click on the map to set goal point'
    if (hasPath) return 'Path computed successfully'
    if (hasGoalPoint && hasStartPoint) return 'Computing path...'
    return 'Ready'
  }

  const getStatusColor = () => {
    if (!hasImage) return 'bg-muted text-muted-foreground'
    if (hasPath) return 'bg-green-500/20 text-green-400'
    if (selectionMode !== 'idle') return 'bg-primary/20 text-primary'
    return 'bg-muted text-muted-foreground'
  }

  return (
    <Card className="border-border bg-card">
      <CardHeader className="pb-4">
        <CardTitle className="flex items-center justify-between text-lg">
          <span>Controls</span>
          <Badge className={cn('font-normal', getStatusColor())}>
            {getStatusText()}
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Upload Section */}
        <div className="space-y-2">
          <label className="text-sm font-medium text-foreground">
            Satellite Image
          </label>
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleFileChange}
            className="hidden"
          />
          <Button
            onClick={() => fileInputRef.current?.click()}
            variant="outline"
            className="w-full justify-start gap-2"
            disabled={isLoading}
          >
            <Upload className="h-4 w-4" />
            {hasImage ? 'Replace Image' : 'Upload Image'}
          </Button>
        </div>

        {/* Point Status */}
        {hasImage && (
          <div className="space-y-3">
            <label className="text-sm font-medium text-foreground">
              Points
            </label>
            <div className="grid grid-cols-2 gap-2">
              <div
                className={cn(
                  'flex items-center gap-2 rounded-lg border px-3 py-2',
                  hasStartPoint
                    ? 'border-green-500/50 bg-green-500/10'
                    : selectionMode === 'selecting-start'
                      ? 'border-primary bg-primary/10'
                      : 'border-border bg-secondary'
                )}
              >
                <MapPin
                  className={cn(
                    'h-4 w-4',
                    hasStartPoint ? 'text-green-500' : 'text-muted-foreground'
                  )}
                />
                <span className="text-sm">
                  {hasStartPoint ? 'Start Set' : 'Start'}
                </span>
              </div>
              <div
                className={cn(
                  'flex items-center gap-2 rounded-lg border px-3 py-2',
                  hasGoalPoint
                    ? 'border-red-500/50 bg-red-500/10'
                    : selectionMode === 'selecting-goal'
                      ? 'border-primary bg-primary/10'
                      : 'border-border bg-secondary'
                )}
              >
                <Flag
                  className={cn(
                    'h-4 w-4',
                    hasGoalPoint ? 'text-red-500' : 'text-muted-foreground'
                  )}
                />
                <span className="text-sm">
                  {hasGoalPoint ? 'Goal Set' : 'Goal'}
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Overlay Controls */}
        {hasImage && (
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <label className="text-sm font-medium text-foreground">
                Road Overlay
              </label>
              <Button
                variant="ghost"
                size="sm"
                onClick={onToggleOverlay}
                className="h-8 w-8 p-0"
              >
                {showOverlay ? (
                  <Eye className="h-4 w-4" />
                ) : (
                  <EyeOff className="h-4 w-4" />
                )}
              </Button>
            </div>
            <div className="space-y-2">
              <div className="flex items-center justify-between text-xs text-muted-foreground">
                <span>Opacity</span>
                <span>{Math.round(overlayOpacity * 100)}%</span>
              </div>
              <Slider
                value={[overlayOpacity]}
                onValueChange={([value]) => onOpacityChange(value)}
                min={0}
                max={1}
                step={0.1}
                disabled={!showOverlay}
                className="py-2"
              />
            </div>
          </div>
        )}

        {/* Clear Button */}
        {hasImage && (hasStartPoint || hasGoalPoint) && (
          <Button
            onClick={onClearSelection}
            variant="destructive"
            className="w-full gap-2"
            disabled={isLoading}
          >
            <Trash2 className="h-4 w-4" />
            Clear Selection
          </Button>
        )}

        {/* Instructions */}
        <div className="rounded-lg bg-secondary p-3">
          <h4 className="mb-2 text-sm font-medium text-foreground">
            Instructions
          </h4>
          <ul className="space-y-1 text-xs text-muted-foreground">
            <li>1. Upload a satellite image</li>
            <li>2. Click on a road to set start point</li>
            <li>3. Click on another road for goal point</li>
            <li>4. Path will be computed automatically</li>
          </ul>
        </div>
      </CardContent>
    </Card>
  )
}
