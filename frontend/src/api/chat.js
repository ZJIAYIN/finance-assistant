import request from './request'

export const chatApi = {
  // 非流式发送消息
  send(data) {
    return request.post('/chat', data)
  },

  // 流式发送消息 (SSE)
  sendStream(data, onMessage, onDone, onError) {
    const token = localStorage.getItem('token')

    return fetch('/api/chat/stream', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(data)
    }).then(response => {
      if (!response.ok) {
        throw new Error('网络请求失败')
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder()

      function readStream() {
        return reader.read().then(({ done, value }) => {
          if (done) {
            return
          }

          const chunk = decoder.decode(value, { stream: true })
          // 解析SSE格式: data: {...}
          const lines = chunk.split('\n')

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const jsonStr = line.slice(6) // 去掉 'data: '
                const parsed = JSON.parse(jsonStr)

                if (parsed.type === 'content') {
                  onMessage?.(parsed.data)
                } else if (parsed.type === 'done') {
                  onDone?.(parsed.data)
                } else if (parsed.type === 'error') {
                  onError?.(parsed.data)
                }
              } catch (e) {
                // 忽略解析失败的行
              }
            }
          }

          return readStream()
        })
      }

      return readStream()
    }).catch(error => {
      onError?.(error.message)
      throw error
    })
  }
}
