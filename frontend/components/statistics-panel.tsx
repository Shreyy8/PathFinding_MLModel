'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import {
  Activity,
  Route,
  MapPin,
  Network,
  Image as ImageIcon,
  TrendingUp,
} from 'lucide-react'
import type { Statistics } from '@/lib/api-client'

interface StatisticsPanelProps {
  statistics: Statistics | null
  hasPath: boolean
}

export default function StatisticsPanel({
  statistics,
  hasPath,
}: StatisticsPanelProps) {
  if (!statistics) {
    return (
      <Card className="border-border bg-card">
        <CardHeader className="pb-4">
          <CardTitle className="flex items-center gap-2 text-lg">
            <Activity className="h-5 w-5" />
            Statistics
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            Upload an image to see statistics
          </p>
        </CardContent>
      </Card>
    )
  }

  const formatNumber = (num: number | undefined) => {
    if (num === undefined || num === null || isNaN(num)) {
      return '0'
    }
    return num.toLocaleString()
  }

  const formatDistance = (pixels: number | undefined) => {
    if (pixels === undefined || pixels === null || isNaN(pixels)) {
      return '0 px'
    }
    // Assuming 1 pixel ≈ 1 meter for display purposes
    if (pixels < 1000) {
      return `${pixels.toFixed(0)} px`
    }
    return `${(pixels / 1000).toFixed(2)} km`
  }

  return (
    <Card className="border-border bg-card">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-base">
          <Activity className="h-4 w-4" />
          Statistics
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {/* Image Statistics */}
        <div className="space-y-1.5">
          <div className="flex items-center gap-2 text-xs font-medium text-foreground">
            <ImageIcon className="h-3 w-3" />
            Image
          </div>
          <div className="grid grid-cols-2 gap-1.5 text-xs">
            <div className="rounded-lg bg-secondary p-1.5">
              <div className="text-[10px] text-muted-foreground">Dimensions</div>
              <div className="font-medium text-xs">
                {statistics?.image_width || 0} × {statistics?.image_height || 0}
              </div>
            </div>
            <div className="rounded-lg bg-secondary p-1.5">
              <div className="text-[10px] text-muted-foreground">Pixels</div>
              <div className="font-medium text-xs">
                {formatNumber(statistics?.total_pixels)}
              </div>
            </div>
          </div>
        </div>

        <Separator />

        {/* Road Network Statistics */}
        <div className="space-y-1.5">
          <div className="flex items-center gap-2 text-xs font-medium text-foreground">
            <Network className="h-3 w-3" />
            Road Network
          </div>
          <div className="space-y-1.5">
            <div className="rounded-lg bg-secondary p-1.5">
              <div className="flex items-center justify-between">
                <div className="text-[10px] text-muted-foreground">Coverage</div>
                <Badge variant="secondary" className="font-mono text-[10px] h-4 px-1">
                  {(statistics?.road_coverage_percent || 0).toFixed(1)}%
                </Badge>
              </div>
              <div className="mt-1 h-1.5 w-full overflow-hidden rounded-full bg-muted">
                <div
                  className="h-full bg-primary transition-all"
                  style={{
                    width: `${Math.min(statistics?.road_coverage_percent || 0, 100)}%`,
                  }}
                />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-1.5 text-xs">
              <div className="rounded-lg bg-secondary p-1.5">
                <div className="text-[10px] text-muted-foreground">Nodes</div>
                <div className="font-medium text-xs">
                  {formatNumber(statistics?.graph_nodes)}
                </div>
              </div>
              <div className="rounded-lg bg-secondary p-1.5">
                <div className="text-[10px] text-muted-foreground">Edges</div>
                <div className="font-medium text-xs">
                  {formatNumber(statistics?.graph_edges)}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Path Statistics (only shown when path exists) */}
        {hasPath && statistics?.path_length_pixels !== undefined && (
          <>
            <Separator />
            <div className="space-y-1.5">
              <div className="flex items-center gap-2 text-xs font-medium text-foreground">
                <Route className="h-3 w-3" />
                Path
              </div>
              <div className="space-y-1.5">
                <div className="rounded-lg bg-primary/10 p-2">
                  <div className="flex items-center justify-between">
                    <div className="text-[10px] text-muted-foreground">
                      Length
                    </div>
                    <TrendingUp className="h-3 w-3 text-primary" />
                  </div>
                  <div className="mt-0.5 text-lg font-bold text-primary">
                    {formatDistance(statistics?.path_length_pixels)}
                  </div>
                  <div className="text-[10px] text-muted-foreground">
                    {(statistics?.path_length_pixels || 0).toFixed(0)} pixels
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-1.5 text-xs">
                  <div className="rounded-lg bg-secondary p-1.5">
                    <div className="text-[10px] text-muted-foreground">
                      Points
                    </div>
                    <div className="font-medium text-xs">
                      {formatNumber(statistics?.path_waypoints || 0)}
                    </div>
                  </div>
                  <div className="rounded-lg bg-secondary p-1.5">
                    <div className="text-[10px] text-muted-foreground">
                      Avg Seg
                    </div>
                    <div className="font-medium text-xs">
                      {statistics?.path_waypoints && statistics.path_waypoints > 1 && statistics?.path_length_pixels
                        ? (
                            statistics.path_length_pixels /
                            (statistics.path_waypoints - 1)
                          ).toFixed(1)
                        : '0'}{' '}
                      px
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </>
        )}

        {/* Algorithm Info */}
        <Separator />
        <div className="rounded-lg bg-muted p-2">
          <div className="flex items-center gap-1.5 text-[10px] font-medium text-muted-foreground">
            <MapPin className="h-3 w-3" />
            A* Pathfinding • 8-connectivity
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
