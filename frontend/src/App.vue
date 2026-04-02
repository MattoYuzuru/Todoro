<template>
  <div class="shell-root">
    <template v-if="isPublicLayout">
      <main class="auth-layout">
        <section class="auth-visual">
          <div class="auth-visual__panel">
            <p class="eyebrow">Todoro</p>
            <h1 class="display-title auth-display-title">Понятный пульт задач и фокус-сессий.</h1>
            <p class="lead-text">
              Не просто список дел, а живое рабочее пространство: задачи, дедлайны, таймеры и быстрые действия из любой точки интерфейса.
            </p>
            <div class="auth-visual__rail">
              <div class="mini-stat">
                <span>Живые таймеры</span>
                <strong>плавающий блок справа</strong>
              </div>
              <div class="mini-stat">
                <span>Задачи</span>
                <strong>ленты + календарь</strong>
              </div>
              <div class="mini-stat">
                <span>Фокус</span>
                <strong>управление Pomodoro</strong>
              </div>
            </div>
          </div>
        </section>

        <section class="auth-stage">
          <router-view />
        </section>
      </main>
    </template>

    <template v-else>
      <div :class="['app-shell', { 'app-shell--with-dock': hasActiveTimers }]">
        <aside class="app-sidebar">
          <div class="brand-block">
            <p class="eyebrow">Todoro</p>
            <h1>Пульт фокуса</h1>
            <p>Задачи, календарь и таймеры в одном потоке.</p>
          </div>

          <nav class="sidebar-nav">
            <RouterLink v-for="item in navItems" :key="item.name" :to="{ name: item.name }">
              <span>{{ item.label }}</span>
              <small>{{ item.caption }}</small>
            </RouterLink>
          </nav>

          <div class="sidebar-footer panel panel--dense">
            <p class="eyebrow">Пульс системы</p>
            <div class="sidebar-footer__stats">
              <div>
                <span>Активно</span>
                <strong>{{ todoStore.openTodos.length }}</strong>
              </div>
              <div>
                <span>Таймеры</span>
                <strong>{{ timerStore.activeTimers.length }}</strong>
              </div>
            </div>
            <button class="button button--ghost" @click="logoutUser">
              Выйти
            </button>
          </div>
        </aside>

        <main class="app-main">
          <header class="topbar panel panel--dense">
            <div>
              <p class="eyebrow">Сегодня</p>
              <h2>
                {{ topbarTitle }}
              </h2>
            </div>

            <div class="topbar__actions">
              <div class="pill-counter">
                <span>{{ todoStore.dueTodayTodos.length }}</span>
                дедлайн(ов) сегодня
              </div>
              <div class="pill-counter">
                <span>{{ timerStore.activeTimers.length }}</span>
                таймер(ов) в боковом эфире
              </div>
              <RouterLink class="button button--accent" :to="{ name: 'create-todo' }">
                Новая задача
              </RouterLink>
            </div>
          </header>

          <router-view />
        </main>
      </div>

      <TimerDock />
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, watch } from "vue";
import { RouterLink, useRoute, useRouter } from "vue-router";

import TimerDock from "./components/TimerDock.vue";
import { useAuthStore, useTimerStore, useTodoStore } from "./store";

const authStore = useAuthStore();
const todoStore = useTodoStore();
const timerStore = useTimerStore();
const route = useRoute();
const router = useRouter();

const navItems = [
  { name: "home", label: "Дашборд", caption: "обзор дня" },
  { name: "todo-list", label: "Задачи", caption: "все карточки" },
  { name: "calendar", label: "Календарь", caption: "расклад по датам" },
  { name: "user-account", label: "Аккаунт", caption: "профиль и настройки" },
];

const isPublicLayout = computed(() => Boolean(route.meta.public) && !authStore.isAuthenticated);
const hasActiveTimers = computed(() => timerStore.activeTimers.length > 0);
const topbarTitle = computed(() => {
  const username = authStore.user?.username ?? "пространство";
  return `Привет, ${username}. Держим фокус под контролем.`;
});

async function bootstrapWorkspace(force = false) {
  if (!authStore.isAuthenticated) {
    return;
  }

  const profile = await authStore.fetchUser();
  if (!profile) {
    return;
  }

  const todos = await todoStore.fetchTodos({ force });
  await timerStore.hydrateForTodos(todos);
  timerStore.boot();
}

function logoutUser() {
  authStore.logout();
  todoStore.reset();
  timerStore.reset();
  router.push({ name: "login" });
}

onMounted(async () => {
  await bootstrapWorkspace();
});

watch(
  () => authStore.isAuthenticated,
  async (isAuthenticated) => {
    if (isAuthenticated) {
      await bootstrapWorkspace(true);
      return;
    }

    todoStore.reset();
    timerStore.reset();
  },
  { immediate: false }
);

watch(
  () => route.fullPath,
  async () => {
    if (authStore.isAuthenticated && !todoStore.loaded) {
      await bootstrapWorkspace();
    }
  }
);
</script>
