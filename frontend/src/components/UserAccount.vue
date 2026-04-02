<template>
  <section class="page-shell">
    <div class="account-grid">
      <section class="panel account-card">
        <div class="section-heading">
          <div>
            <p class="eyebrow">Профиль</p>
            <h1 style="margin: 0; font-size: 2.5rem; letter-spacing: -0.05em;">{{ user.username }}</h1>
          </div>
          <button class="button button--ghost" @click="logoutUser">
            Выйти
          </button>
        </div>

        <p class="lead-text">
          {{ user.email }}
        </p>

        <div class="stats-grid">
          <article class="metric-card">
            <span>Текущая серия</span>
            <strong>{{ user.current_streak ?? 0 }}</strong>
            <p>Текущий ритм активности по системе.</p>
          </article>
          <article class="metric-card">
            <span>Лучшая серия</span>
            <strong>{{ user.longest_streak ?? 0 }}</strong>
            <p>Пиковая серия без разрыва темпа.</p>
          </article>
          <article class="metric-card">
            <span>Pomodoro</span>
            <strong>{{ user.pomodoro_sessions ?? 0 }}</strong>
            <p>Сколько фокус-циклов уже закрыто.</p>
          </article>
          <article class="metric-card">
            <span>Готовые задачи</span>
            <strong>{{ user.tasks_completed ?? 0 }}</strong>
            <p>Полезный результат, а не просто активность.</p>
          </article>
        </div>
      </section>

      <aside class="panel sticky-panel">
        <div class="form-grid">
          <div class="field-block">
            <label for="email">Новый email</label>
            <input id="email" v-model="email" class="field" type="email" placeholder="new@email.com">
            <button class="button button--accent" @click="updateEmail">
              Обновить email
            </button>
          </div>

          <div class="field-block">
            <label for="password">Новый пароль</label>
            <input id="password" v-model="password" class="field" type="password" placeholder="••••••••">
            <button class="button button--ghost" @click="updatePassword">
              Сменить пароль
            </button>
          </div>

          <div class="danger-card">
            <p class="eyebrow">Опасная зона</p>
            <h3 style="margin: 0 0 10px;">Удаление аккаунта</h3>
            <p>Если удалить аккаунт, все задачи и твой текущий рабочий ритм исчезнут навсегда.</p>
            <button class="button button--danger" @click="showDeletePopup = true">
              Удалить аккаунт
            </button>
          </div>
        </div>
      </aside>
    </div>

    <section v-if="showDeletePopup" class="panel danger-card">
      <div class="section-heading">
        <div>
          <p class="eyebrow">Подтверждение</p>
          <h2>Точно удалить аккаунт?</h2>
        </div>
      </div>
      <p>Это действие необратимо. После удаления придется создавать новый профиль и заново собирать свои задачи.</p>
      <div class="inline-actions">
        <button class="button button--danger" @click="deleteAccount">
          Да, удалить
        </button>
        <button class="button button--ghost" @click="showDeletePopup = false">
          Отмена
        </button>
      </div>
    </section>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";

import api from "../api/client";
import { useAuthStore, useTimerStore, useTodoStore } from "../store";

const authStore = useAuthStore();
const todoStore = useTodoStore();
const timerStore = useTimerStore();
const router = useRouter();

const email = ref("");
const password = ref("");
const showDeletePopup = ref(false);

const user = computed(() => authStore.user ?? {});

async function updateEmail() {
  try {
    await api.put(`/users/${user.value.id}`, { email: email.value });
    email.value = "";
    await authStore.fetchUser();
  } catch (error) {
    console.error("Не удалось обновить email:", error);
  }
}

async function updatePassword() {
  try {
    await api.put(`/users/${user.value.id}`, { password: password.value });
    password.value = "";
  } catch (error) {
    console.error("Не удалось обновить пароль:", error);
  }
}

async function deleteAccount() {
  try {
    await api.delete(`/users/${user.value.id}`);
    logoutUser();
  } catch (error) {
    console.error("Не удалось удалить аккаунт:", error);
  }
}

function logoutUser() {
  authStore.logout();
  todoStore.reset();
  timerStore.reset();
  router.push({ name: "login" });
}

onMounted(async () => {
  const profile = await authStore.fetchUser();
  if (!profile) {
    await router.push({ name: "login" });
  }
});
</script>
