<script setup>
import { ref, computed, reactive, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Menu, Close, Key, SwitchButton, Plus, User, Lock } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const menuVisible = ref(false)
const accountDialogVisible = ref(false)
const pwdSubmitting = ref(false)
const pwdForm = reactive({
  current: '',
  new1: '',
  new2: ''
})

const roleLabel = computed(() => {
  const r = auth.user?.role
  if (r === 'admin') return '管理员'
  if (r === 'user') return '普通用户'
  return r || '—'
})

function formatCreated(iso) {
  if (!iso) return '—'
  try {
    const d = new Date(iso)
    if (Number.isNaN(d.getTime())) return iso
    return d.toLocaleString('zh-CN', { dateStyle: 'medium', timeStyle: 'short' })
  } catch {
    return iso
  }
}

function resetPwdForm() {
  pwdForm.current = ''
  pwdForm.new1 = ''
  pwdForm.new2 = ''
}

function openAccountPanel() {
  menuVisible.value = false
  resetPwdForm()
  accountDialogVisible.value = true
}

watch(accountDialogVisible, (open) => {
  if (!open) resetPwdForm()
})

async function submitPasswordChange() {
  if (!pwdForm.current) {
    ElMessage.warning('请输入当前密码')
    return
  }
  if (!pwdForm.new1 || pwdForm.new1.length < 6) {
    ElMessage.warning('新密码至少 6 位')
    return
  }
  if (pwdForm.new1 !== pwdForm.new2) {
    ElMessage.warning('两次输入的新密码不一致')
    return
  }
  pwdSubmitting.value = true
  try {
    await auth.changePassword(pwdForm.current, pwdForm.new1)
    resetPwdForm()
    ElMessage.success('密码已更新')
  } catch (e) {
    const msg = e?.response?.data?.detail
    ElMessage.error(typeof msg === 'string' ? msg : e?.message || '修改失败')
  } finally {
    pwdSubmitting.value = false
  }
}

function onLogoutFromPanel() {
  accountDialogVisible.value = false
  onLogout()
}

const allNavItems = [
  { path: '/', name: '首页' },
  { path: '/chat', name: '智能问答' },
  { path: '/component', name: '组件管理' },
  { path: '/knowledge', name: '知识库', requiresAdmin: true },
  { path: '/admin/users', name: '用户管理', requiresAdmin: true }
]

const navItems = computed(() =>
  allNavItems.filter((item) => !item.requiresAdmin || auth.isAdmin)
)

const isActive = (path) => {
  if (path === '/') return route.path === '/'
  return route.path.startsWith(path)
}

const goTo = (path) => {
  menuVisible.value = false
  router.push(path)
}

const goLogin = () => {
  menuVisible.value = false
  router.push({ path: '/login', query: { redirect: route.fullPath } })
}

const goRegister = () => {
  menuVisible.value = false
  router.push('/register')
}

const onLogout = () => {
  menuVisible.value = false
  auth.logout()
  router.push('/')
}

const isMobile = computed(() => {
  if (typeof window === 'undefined') return false
  return window.innerWidth < 768
})
</script>

<template>
  <div class="app-wrap">
    <header class="app-header">
      <div class="header-inner">
        <router-link to="/" class="logo-area" @click="menuVisible = false">
          <div class="logo-icon">
            <svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
              <rect width="40" height="40" rx="10" fill="url(#logoGrad)" />
              <path d="M12 20h16M12 14h10M12 26h14" stroke="white" stroke-width="2" stroke-linecap="round" />
              <defs>
                <linearGradient id="logoGrad" x1="0" y1="0" x2="40" y2="40" gradientUnits="userSpaceOnUse">
                  <stop stop-color="#0EA5E9" />
                  <stop offset="1" stop-color="#38BDF8" />
                </linearGradient>
              </defs>
            </svg>
          </div>
          <div class="logo-text">
            <span class="logo-zh">轨道交通知识服务系统</span>
            <span class="logo-en">Rail Transit Knowledge Service</span>
          </div>
        </router-link>

        <nav class="nav-menu" :class="{ open: menuVisible }">
          <a
            v-for="item in navItems"
            :key="item.path"
            :href="item.path"
            :class="['nav-item', { active: isActive(item.path) }]"
            @click.prevent="goTo(item.path)"
          >
            {{ item.name }}
          </a>
          <div v-if="isMobile" class="nav-auth-mobile">
            <div class="nav-auth-divider" />
            <template v-if="auth.isAuthenticated">
              <div class="nav-user-row">
                <span class="user-avatar-sm">{{ (auth.user?.username || '?').charAt(0).toUpperCase() }}</span>
                <span class="nav-user-name">{{ auth.user?.username }}</span>
              </div>
              <el-button class="header-auth-btn is-block" plain @click="openAccountPanel">
                <el-icon><User /></el-icon>
                个人中心
              </el-button>
            </template>
            <template v-else>
              <el-button class="header-auth-btn is-block" plain @click="goLogin">
                <el-icon><Key /></el-icon>
                登录
              </el-button>
              <el-button class="header-auth-btn is-block" plain @click="goRegister">
                <el-icon><Plus /></el-icon>
                注册
              </el-button>
            </template>
          </div>
        </nav>

        <div class="header-actions">
          <div class="auth-cluster" :class="{ 'auth-cluster--hidden-mobile': isMobile }">
            <template v-if="auth.isAuthenticated">
              <button
                type="button"
                class="user-pill user-pill--clickable"
                :title="auth.user?.username + ' — 个人中心'"
                @click="openAccountPanel"
              >
                <span class="user-avatar">{{ (auth.user?.username || '?').charAt(0).toUpperCase() }}</span>
                <span class="user-pill-name">{{ auth.user?.username }}</span>
              </button>
            </template>
            <template v-else>
              <el-button class="header-auth-btn" plain @click="goLogin">
                <el-icon><Key /></el-icon>
                登录
              </el-button>
              <el-button class="header-auth-btn" plain @click="goRegister">
                <el-icon><Plus /></el-icon>
                注册
              </el-button>
            </template>
          </div>
          <button type="button" class="hamburger" aria-label="菜单" @click="menuVisible = !menuVisible">
            <el-icon v-if="!menuVisible"><Menu /></el-icon>
            <el-icon v-else><Close /></el-icon>
          </button>
        </div>
      </div>
    </header>

    <main class="app-main">
      <router-view v-slot="{ Component, route: currentRoute }">
        <transition name="fade" mode="out-in">
          <component 
            :is="Component" 
            :key="currentRoute.path"
          />
        </transition>
      </router-view>
    </main>

    <el-dialog
      v-model="accountDialogVisible"
      width="440px"
      class="account-dialog"
      destroy-on-close
      align-center
      append-to-body
      :show-close="true"
    >
      <template #header>
        <div v-if="auth.user" class="account-dialog-header">
          <div class="account-header-avatar" aria-hidden="true">
            {{ (auth.user.username || '?').charAt(0).toUpperCase() }}
          </div>
          <div class="account-header-meta">
            <span class="account-header-name">{{ auth.user.username }}</span>
            <span :class="['account-role-badge', auth.user.role === 'admin' ? 'is-admin' : 'is-user']">
              {{ roleLabel }}
            </span>
          </div>
        </div>
      </template>

      <template v-if="auth.user">
        <div class="account-dialog-body">
          <div class="account-card account-card--info">
            <span class="account-card-label">注册时间</span>
            <span class="account-card-value">{{ formatCreated(auth.user.created_at) }}</span>
          </div>

          <div class="account-card account-card--pwd">
            <div class="account-card-head">
              <el-icon class="account-card-icon"><Lock /></el-icon>
              <span class="account-card-title">修改密码</span>
            </div>
            <el-form
              label-position="top"
              size="default"
              class="account-pwd-form"
              @submit.prevent="submitPasswordChange"
            >
              <el-form-item label="当前密码">
                <el-input
                  v-model="pwdForm.current"
                  type="password"
                  show-password
                  autocomplete="current-password"
                  placeholder="请输入当前登录密码"
                />
              </el-form-item>
              <el-form-item label="新密码（至少 6 位）">
                <el-input
                  v-model="pwdForm.new1"
                  type="password"
                  show-password
                  autocomplete="new-password"
                  placeholder="新密码"
                />
              </el-form-item>
              <el-form-item label="确认新密码">
                <el-input
                  v-model="pwdForm.new2"
                  type="password"
                  show-password
                  autocomplete="new-password"
                  placeholder="再次输入新密码"
                />
              </el-form-item>
              <el-button type="primary" :loading="pwdSubmitting" native-type="submit" class="account-pwd-submit">
                保存新密码
              </el-button>
            </el-form>
          </div>
        </div>
      </template>

      <template #footer>
        <div class="account-dialog-footer">
          <el-button plain class="account-footer-btn" @click="accountDialogVisible = false">关闭</el-button>
          <el-button type="danger" plain class="account-footer-btn" @click="onLogoutFromPanel">
            <el-icon><SwitchButton /></el-icon>
            退出登录
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped lang="scss">
.app-wrap {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  position: sticky;
  top: 0;
  z-index: 1000;
  height: var(--nav-height);
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(226, 232, 240, 0.8);
  box-shadow: var(--shadow-lg);
}

.header-inner {
  max-width: var(--content-max-width);
  margin: 0 auto;
  height: 100%;
  padding: 0 var(--padding-inline);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
}

.logo-area {
  display: flex;
  align-items: center;
  gap: 12px;
  text-decoration: none;
  color: var(--gray-900);
}

.logo-icon {
  width: 40px;
  height: 40px;
  flex-shrink: 0;
}

.logo-icon svg {
  width: 100%;
  height: 100%;
  display: block;
}

.logo-text {
  display: flex;
  flex-direction: column;
  line-height: 1.3;
}

.logo-zh {
  font-size: 16px;
  font-weight: 600;
  color: var(--gray-900);
}

.logo-en {
  font-size: 11px;
  color: var(--gray-500);
}

.nav-menu {
  display: flex;
  align-items: center;
  gap: 8px;
}

.nav-item {
  padding: 8px 16px;
  border-radius: var(--button-radius);
  color: var(--gray-600);
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  transition: var(--transition-fast);
}

.nav-item:hover {
  color: var(--primary-500);
  background: rgba(14, 165, 233, 0.08);
}

.nav-item.active {
  color: var(--primary-500);
  background: rgba(14, 165, 233, 0.12);
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

.auth-cluster {
  display: flex;
  align-items: center;
  gap: 8px;
}

.auth-cluster--hidden-mobile {
  display: none !important;
}

.user-pill {
  display: none;
  align-items: center;
  gap: 10px;
  max-width: 220px;
  padding: 6px 12px 6px 6px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid var(--gray-200);
  box-shadow: 0 1px 3px rgba(15, 23, 42, 0.06);
}

.user-pill--clickable {
  cursor: pointer;
  font: inherit;
  color: inherit;
  transition: var(--transition-fast);
}

.user-pill--clickable:hover {
  border-color: var(--primary-400, #38bdf8);
  box-shadow: 0 2px 8px rgba(14, 165, 233, 0.15);
}

@media (min-width: 900px) {
  .user-pill {
    display: inline-flex;
  }
}

.user-avatar {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  font-size: 14px;
  font-weight: 700;
  color: #fff;
  background: var(--primary-gradient);
  flex-shrink: 0;
}

.user-pill-name {
  font-size: 13px;
  font-weight: 600;
  color: var(--gray-900);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.action-button.ghost {
  border: 1px solid var(--gray-200);
  background: transparent;
  color: var(--gray-700);
}

.nav-auth-mobile {
  display: none;
}

.nav-auth-divider {
  height: 1px;
  margin: 8px 0 4px;
  background: var(--gray-200);
}

.nav-user-row {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 4px 4px;
}

.user-avatar-sm {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  font-size: 15px;
  font-weight: 700;
  color: #fff;
  background: var(--primary-gradient);
}

.nav-user-name {
  font-weight: 600;
  color: var(--gray-900);
  font-size: 15px;
}

.hamburger {
  display: none;
  padding: 8px;
  border: none;
  background: none;
  cursor: pointer;
  color: var(--gray-600);
  font-size: 20px;
}

.app-main {
  flex: 1;
  position: relative;
  overflow: visible; /* 确保内容可以正常显示 */
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity var(--transition-normal);
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@media (max-width: 1024px) {
  .nav-menu {
    gap: 4px;
  }
  .nav-item {
    padding: 8px 12px;
    font-size: 13px;
  }
}

@media (max-width: 768px) {
  .nav-menu {
    position: fixed;
    top: var(--nav-height);
    left: 0;
    right: 0;
    flex-direction: column;
    background: var(--bg-card);
    backdrop-filter: blur(20px);
    padding: 16px;
    gap: 4px;
    box-shadow: var(--shadow-lg);
    border-bottom: 1px solid var(--gray-200);
    transform: translateY(-100%);
    opacity: 0;
    visibility: hidden;
    transition: var(--transition-normal);
  }

  .nav-menu.open {
    transform: translateY(0);
    opacity: 1;
    visibility: visible;
  }

  .nav-item {
    width: 100%;
    padding: 12px 16px;
    text-align: left;
  }

  .nav-auth-mobile {
    display: flex;
    flex-direction: column;
    gap: 8px;
    width: 100%;
    padding-top: 4px;
  }

  .hamburger {
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .logo-en {
    display: none;
  }
}

</style>

<!-- el-dialog teleport 到 body，需非 scoped 样式 -->
<style lang="scss">
.account-dialog.el-dialog {
  border-radius: var(--card-radius-lg, 18px);
  border: 1px solid var(--gray-200, #e2e8f0);
  box-shadow: var(--shadow-lg, 0 12px 40px rgba(15, 23, 42, 0.12));
  overflow: hidden;
}

.account-dialog .el-dialog__header {
  margin: 0;
  padding: 0;
  border-bottom: 1px solid var(--gray-200, #e2e8f0);
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.96) 0%, var(--bg-primary, #f8fafc) 100%);
}

.account-dialog .el-dialog__headerbtn {
  top: 16px;
  right: 16px;
}

.account-dialog .el-dialog__body {
  padding: 16px 20px 8px;
  background: var(--bg-primary, #f8fafc);
}

.account-dialog .el-dialog__footer {
  padding: 12px 20px 20px;
  background: var(--bg-primary, #f8fafc);
  border-top: 1px solid var(--gray-200, #e2e8f0);
}

.account-dialog-header {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 20px 44px 18px 20px;
}

.account-header-avatar {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: 700;
  color: #fff;
  background: var(--primary-gradient, linear-gradient(135deg, #0ea5e9 0%, #38bdf8 100%));
  flex-shrink: 0;
  box-shadow: var(--shadow-sm, 0 2px 8px rgba(14, 165, 233, 0.35));
}

.account-header-meta {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 0;
}

.account-header-name {
  font-size: 17px;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: var(--gray-900, #0f172a);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.account-role-badge {
  align-self: flex-start;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
  border: 1px solid transparent;
}

.account-role-badge.is-admin {
  color: #0f172a;
  background: rgba(14, 165, 233, 0.12);
  border-color: rgba(14, 165, 233, 0.35);
}

.account-role-badge.is-user {
  color: var(--gray-600, #475569);
  background: rgba(255, 255, 255, 0.85);
  border-color: var(--gray-200, #e2e8f0);
}

.account-dialog-body {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.account-card {
  border-radius: var(--card-radius, 12px);
  border: 1px solid var(--gray-200, #e2e8f0);
  background: var(--bg-card, rgba(255, 255, 255, 0.92));
  box-shadow: var(--shadow-sm, 0 1px 3px rgba(0, 0, 0, 0.06));
}

.account-card--info {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 14px 16px;
}

.account-card-label {
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--gray-500, #64748b);
}

.account-card-value {
  font-size: 14px;
  font-weight: 500;
  color: var(--gray-900, #0f172a);
}

.account-card--pwd {
  padding: 16px 16px 18px;
}

.account-card-head {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 14px;
}

.account-card-icon {
  font-size: 18px;
  color: var(--primary-500, #0ea5e9);
}

.account-card-title {
  font-size: 15px;
  font-weight: 700;
  color: var(--gray-900, #0f172a);
  letter-spacing: -0.01em;
}

.account-dialog .account-pwd-form {
  max-width: 100%;
}

.account-dialog .account-pwd-form :deep(.el-form-item) {
  margin-bottom: 14px;
}

.account-dialog .account-pwd-form :deep(.el-form-item__label) {
  font-weight: 600;
  font-size: 13px;
  color: var(--gray-900, #0f172a);
}

.account-dialog .account-pwd-form :deep(.el-input__wrapper) {
  border-radius: var(--button-radius, 12px);
}

.account-dialog .account-pwd-submit {
  width: 100%;
  margin-top: 6px;
  height: 42px;
  border-radius: var(--button-radius, 12px);
  font-weight: 600;
}

.account-dialog-footer {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 10px;
  width: 100%;
}

.account-footer-btn {
  border-radius: var(--button-radius, 12px);
  font-weight: 600;
}
</style>
