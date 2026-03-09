'use client'

import { useEffect } from 'react'
import { X, CheckCircle, AlertCircle, Info, Loader2 } from 'lucide-react'
import { cn } from '@/lib/utils'

export type NotificationType = 'success' | 'error' | 'info' | 'loading'

export interface Notification {
  id: string
  type: NotificationType
  message: string
  autoDismiss?: boolean
}

interface NotificationItemProps {
  notification: Notification
  onDismiss: (id: string) => void
}

function NotificationItem({ notification, onDismiss }: NotificationItemProps) {
  const { id, type, message, autoDismiss } = notification

  useEffect(() => {
    if (autoDismiss && type !== 'loading') {
      const timer = setTimeout(() => {
        onDismiss(id)
      }, 4000)
      return () => clearTimeout(timer)
    }
  }, [id, autoDismiss, onDismiss, type])

  const icons = {
    success: <CheckCircle className="h-5 w-5" />,
    error: <AlertCircle className="h-5 w-5" />,
    info: <Info className="h-5 w-5" />,
    loading: <Loader2 className="h-5 w-5 animate-spin" />,
  }

  const styles = {
    success: 'bg-green-500/90 text-white',
    error: 'bg-red-500/90 text-white',
    info: 'bg-primary/90 text-primary-foreground',
    loading: 'bg-secondary text-secondary-foreground',
  }

  return (
    <div
      className={cn(
        'flex items-center gap-3 rounded-lg px-4 py-3 shadow-lg backdrop-blur-sm',
        'animate-in slide-in-from-right-5 fade-in duration-300',
        styles[type]
      )}
    >
      {icons[type]}
      <p className="flex-1 text-sm font-medium">{message}</p>
      {type !== 'loading' && (
        <button
          onClick={() => onDismiss(id)}
          className="rounded p-1 transition-colors hover:bg-white/20"
        >
          <X className="h-4 w-4" />
        </button>
      )}
    </div>
  )
}

interface NotificationsContainerProps {
  notifications: Notification[]
  onDismiss: (id: string) => void
}

export function NotificationsContainer({
  notifications,
  onDismiss,
}: NotificationsContainerProps) {
  return (
    <div className="fixed right-4 top-4 z-50 flex w-80 flex-col gap-2">
      {notifications.map((notification) => (
        <NotificationItem
          key={notification.id}
          notification={notification}
          onDismiss={onDismiss}
        />
      ))}
    </div>
  )
}

// Hook for managing notifications
import { useState, useCallback } from 'react'

export function useNotifications() {
  const [notifications, setNotifications] = useState<Notification[]>([])

  const addNotification = useCallback(
    (
      type: NotificationType,
      message: string,
      autoDismiss: boolean = type === 'success' || type === 'info'
    ) => {
      const id = `${Date.now()}-${Math.random().toString(36).slice(2)}`
      setNotifications((prev) => [...prev, { id, type, message, autoDismiss }])
      return id
    },
    []
  )

  const dismissNotification = useCallback((id: string) => {
    setNotifications((prev) => prev.filter((n) => n.id !== id))
  }, [])

  const showSuccess = useCallback(
    (message: string) => addNotification('success', message),
    [addNotification]
  )

  const showError = useCallback(
    (message: string) => addNotification('error', message, false),
    [addNotification]
  )

  const showInfo = useCallback(
    (message: string) => addNotification('info', message),
    [addNotification]
  )

  const showLoading = useCallback(
    (message: string) => addNotification('loading', message, false),
    [addNotification]
  )

  const hideLoading = useCallback(
    (id: string) => dismissNotification(id),
    [dismissNotification]
  )

  const clearAll = useCallback(() => {
    setNotifications([])
  }, [])

  return {
    notifications,
    showSuccess,
    showError,
    showInfo,
    showLoading,
    hideLoading,
    dismissNotification,
    clearAll,
  }
}
