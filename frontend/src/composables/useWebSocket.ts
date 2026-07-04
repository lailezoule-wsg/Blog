import { ref, onUnmounted } from 'vue'
import { ElNotification } from 'element-plus'

interface ConnectedMessage {
  type: 'connected'
  data: { message: string; user_id: number; connected_at: string }
}

interface NewCommentMessage {
  type: 'new_comment'
  data: { article_id: number; comment_id: number; commenter: string; content: string; created_at: string }
}

interface ArticlePublishedMessage {
  type: 'article_published'
  data: { article_id: number; title: string; author: string; published_at: string }
}

type WSMessage = ConnectedMessage | NewCommentMessage | ArticlePublishedMessage | { type: 'ping' | 'pong_check' }

interface UseWebSocketOptions {
  maxRetries?: number
  retryDelay?: number
}

export function useWebSocket(options: UseWebSocketOptions = {}) {
  const { maxRetries = 5, retryDelay = 3000 } = options

  const isConnected = ref(false)
  const messages = ref<WSMessage[]>([])
  let ws: WebSocket | null = null
  let retryCount = 0
  let retryTimer: ReturnType<typeof setTimeout> | null = null
  let disposed = false

  function getToken(): string | null {
    return localStorage.getItem('token') || null
  }

  function connect() {
    if (ws || disposed) return

    const token = getToken()
    if (!token) {
      console.warn('WS: no token, skip connect')
      return
    }

    const wsUrl = `ws://localhost:8000/ws/notifications?token=${encodeURIComponent(token)}`
    ws = new WebSocket(wsUrl)

    ws.onopen = () => {
      isConnected.value = true
      retryCount = 0
      console.log('WS: connected')
    }

    ws.onmessage = (event) => {
      let msg: WSMessage
      try {
        msg = JSON.parse(event.data)
      } catch {
        return
      }

      switch (msg.type) {
        case 'ping':
          ws?.send(JSON.stringify({ type: 'pong' }))
          break
        case 'pong_check':
          break
        case 'connected':
          console.log('WS: auth confirmed, user_id =', msg.data.user_id)
          break
        case 'new_comment': {
          messages.value.push(msg)
          ElNotification({
            title: '新评论',
            message: `${msg.data.commenter} 评论了: ${msg.data.content}`,
            type: 'info',
            duration: 5000,
          })
          break
        }
        case 'article_published': {
          messages.value.push(msg)
          ElNotification({
            title: '新文章',
            message: `${msg.data.author} 发布了: ${msg.data.title}`,
            type: 'success',
            duration: 5000,
          })
          break
        }
      }
    }

    ws.onclose = (event) => {
      isConnected.value = false
      console.log(`WS: closed (code=${event.code})`)

      if (disposed) return

      if (event.code === 4001 || event.code === 4002) {
        console.warn('WS: auth failed, will not reconnect')
        return
      }

      if (retryCount < maxRetries) {
        retryCount++
        const delay = Math.min(retryDelay * Math.pow(1.5, retryCount - 1), 30000)
        console.log(`WS: reconnecting in ${delay}ms (attempt ${retryCount}/${maxRetries})`)
        retryTimer = setTimeout(connect, delay)
      } else {
        console.warn('WS: max retries reached')
      }
    }

    ws.onerror = (error) => {
      console.error('WS: error', error)
    }
  }

  function disconnect() {
    disposed = false
    if (retryTimer) {
      clearTimeout(retryTimer)
      retryTimer = null
    }
    if (ws) {
      ws.close(1000)
      ws = null
    }
    isConnected.value = false
  }

  onUnmounted(() => {
    disposed = true
    if (retryTimer) {
      clearTimeout(retryTimer)
      retryTimer = null
    }
    if (ws) {
      ws.close(1000)
      ws = null
    }
  })

  return {
    isConnected,
    messages,
    connect,
    disconnect,
  }
}
