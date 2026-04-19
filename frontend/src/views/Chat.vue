<template>
  <div class="chat-container">
    <!-- 左侧会话列表 -->
    <aside class="sidebar">
      <div class="sidebar-header">
        <el-button
          type="primary"
          @click="createNewSession"
          :icon="Plus"
          style="width: 100%"
        >
          新建会话
        </el-button>
      </div>

      <div class="session-list">
        <div
          v-for="session in chatStore.sessions"
          :key="session.id"
          :class="['session-item', { active: session.id === chatStore.currentSessionId }]"
          @click="selectSession(session.id)"
        >
          <el-icon><ChatDotRound /></el-icon>
          <span class="session-name">{{ session.session_name }}</span>
          <el-dropdown @command="handleCommand($event, session)" @click.stop>
            <el-icon class="more-icon"><More /></el-icon>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="rename">重命名</el-dropdown-item>
                <el-dropdown-item command="delete" divided>删除</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>

        <el-empty v-if="chatStore.sessions.length === 0" description="暂无会话" />
      </div>

      <div class="sidebar-footer">
        <el-dropdown @command="handleUserCommand">
          <span class="user-info">
            <el-icon><User /></el-icon>
            {{ userStore.userInfo?.username || '用户' }}
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </aside>

    <!-- 右侧聊天区域 -->
    <main class="chat-main">
      <!-- 消息列表 -->
      <div class="message-list" ref="messageListRef">
        <template v-if="chatStore.messages.length > 0">
          <div
            v-for="msg in chatStore.messages"
            :key="msg.id"
            :class="['message', msg.role]"
          >
            <div class="message-avatar">
              <el-avatar
                :size="40"
                :icon="msg.role === 'user' ? User : Service"
                :style="{ background: msg.role === 'user' ? '#409EFF' : '#67C23A' }"
              />
            </div>
            <div class="message-content">
              <div class="message-bubble" v-html="formatMessage(msg.content)"></div>
              <div v-if="msg.dataDate" class="message-meta">
                数据来源: {{ msg.dataDate }}
                <span v-if="msg.retrievedCount !== undefined">
                  | 检索到 {{ msg.retrievedCount }} 条相关信息
                </span>
              </div>
            </div>
          </div>
        </template>

        <el-empty
          v-else
          description="开始一个新的对话吧"
          :image-size="100"
        />

        <div v-if="chatStore.loading" class="loading-indicator">
          <el-icon class="is-loading"><Loading /></el-icon>
          思考中...
        </div>
      </div>

      <!-- 输入区域 -->
      <div class="input-area">
        <el-input
          v-model="inputMessage"
          type="textarea"
          :rows="3"
          placeholder="输入您的问题..."
          resize="none"
          @keyup.enter.ctrl="sendMessage"
        />
        <div class="input-actions">
          <span class="hint">Ctrl + Enter 发送</span>
          <el-button
            type="primary"
            @click="sendMessage"
            :loading="chatStore.loading"
            :disabled="!inputMessage.trim()"
          >
            发送
          </el-button>
        </div>
      </div>
    </main>

    <!-- 重命名对话框 -->
    <el-dialog v-model="renameDialogVisible" title="重命名会话" width="400px">
      <el-input v-model="newSessionName" placeholder="请输入新名称" />
      <template #footer>
        <el-button @click="renameDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmRename">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, ChatDotRound, More, User, Service, Loading
} from '@element-plus/icons-vue'
import { marked } from 'marked'
import { useUserStore } from '../stores/user'
import { useChatStore } from '../stores/chat'

const router = useRouter()
const userStore = useUserStore()
const chatStore = useChatStore()

const inputMessage = ref('')
const messageListRef = ref()
const renameDialogVisible = ref(false)
const newSessionName = ref('')
const currentEditingSession = ref(null)

// 格式化消息（Markdown）
const formatMessage = (content) => {
  if (!content) return ''
  return marked(content)
}

// 滚动到底部
const scrollToBottom = () => {
  nextTick(() => {
    if (messageListRef.value) {
      messageListRef.value.scrollTop = messageListRef.value.scrollHeight
    }
  })
}

// 监听消息变化，自动滚动
watch(() => chatStore.messages.length, scrollToBottom)

// 创建新会话
const createNewSession = async () => {
  await chatStore.createSession()
  inputMessage.value = ''
}

// 选择会话
const selectSession = async (sessionId) => {
  await chatStore.selectSession(sessionId)
  scrollToBottom()
}

// 发送消息
const sendMessage = async () => {
  const message = inputMessage.value.trim()
  if (!message || chatStore.loading) return

  inputMessage.value = ''
  await chatStore.sendMessage(message)
}

// 会话操作
const handleCommand = (command, session) => {
  if (command === 'rename') {
    currentEditingSession.value = session
    newSessionName.value = session.session_name
    renameDialogVisible.value = true
  } else if (command === 'delete') {
    ElMessageBox.confirm('确定要删除这个会话吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }).then(async () => {
      await chatStore.deleteSession(session.id)
      ElMessage.success('删除成功')
    })
  }
}

// 确认重命名
const confirmRename = async () => {
  if (!newSessionName.value.trim()) {
    ElMessage.warning('名称不能为空')
    return
  }
  await chatStore.updateSessionName(
    currentEditingSession.value.id,
    newSessionName.value
  )
  renameDialogVisible.value = false
  ElMessage.success('重命名成功')
}

// 用户操作
const handleUserCommand = (command) => {
  if (command === 'logout') {
    userStore.logout()
    router.push('/login')
  }
}

// 初始化
onMounted(async () => {
  // 获取用户信息
  if (!userStore.userInfo) {
    await userStore.fetchUserInfo()
  }
  // 获取会话列表
  await chatStore.fetchSessions()
})
</script>

<style scoped>
.chat-container {
  display: flex;
  height: 100vh;
  background: #f5f5f5;
}

/* 侧边栏 */
.sidebar {
  width: 260px;
  background: #fff;
  border-right: 1px solid #e0e0e0;
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding: 16px;
  border-bottom: 1px solid #e0e0e0;
}

.session-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.session-item {
  display: flex;
  align-items: center;
  padding: 12px;
  margin-bottom: 4px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
}

.session-item:hover {
  background: #f0f0f0;
}

.session-item.active {
  background: #e6f2ff;
}

.session-name {
  flex: 1;
  margin-left: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.more-icon {
  padding: 4px;
  border-radius: 4px;
}

.more-icon:hover {
  background: #ddd;
}

.sidebar-footer {
  padding: 16px;
  border-top: 1px solid #e0e0e0;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  gap: 8px;
}

/* 聊天主区域 */
.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #fff;
}

.message-list {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.message {
  display: flex;
  margin-bottom: 20px;
  gap: 12px;
}

.message.user {
  flex-direction: row-reverse;
}

.message-content {
  max-width: 70%;
}

.message-bubble {
  padding: 12px 16px;
  border-radius: 12px;
  background: #f0f0f0;
  line-height: 1.6;
}

.message.user .message-bubble {
  background: #409EFF;
  color: #fff;
}

.message-meta {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
}

.loading-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: #666;
  padding: 20px;
}

/* 输入区域 */
.input-area {
  padding: 16px 20px;
  border-top: 1px solid #e0e0e0;
  background: #fff;
}

.input-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
}

.hint {
  font-size: 12px;
  color: #999;
}
</style>
