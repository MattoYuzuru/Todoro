<template>
  <section class="auth-panel">
    <p class="eyebrow">Регистрация</p>
    <h2>Собери себе новое рабочее пространство</h2>
    <p class="lead-text">
      После регистрации можно сразу создавать задачи, запускать `Pomodoro` и видеть live-таймеры в боковом стеке интерфейса.
    </p>

    <form class="form-grid" @submit.prevent="register">
      <div class="field-block">
        <label for="username">Username</label>
        <input id="username" v-model="username" type="text" class="field" required>
      </div>

      <div class="field-block">
        <label for="email">Email</label>
        <input id="email" v-model="email" type="email" class="field" required>
      </div>

      <div class="field-block">
        <label for="password">Password</label>
        <input id="password" v-model="password" type="password" class="field" required>
      </div>

      <div class="auth-actions">
        <button type="submit" class="button button--accent">Зарегистрироваться</button>
        <RouterLink class="button button--ghost" :to="{ name: 'login' }">
          Уже есть аккаунт
        </RouterLink>
      </div>
    </form>

    <p v-if="errorMessage" class="chip" data-tone="danger" style="margin-top: 16px;">
      {{ errorMessage }}
    </p>
  </section>
</template>

<script setup>
import { ref } from "vue";
import { RouterLink, useRouter } from "vue-router";

import api from "../api/client";

const router = useRouter();

const username = ref("");
const email = ref("");
const password = ref("");
const errorMessage = ref("");

async function register() {
  try {
    await api.post("/create", {
      username: username.value,
      email: email.value,
      password: password.value,
    });
    await router.push({ name: "login" });
  } catch (error) {
    errorMessage.value = error.response?.data?.detail ?? "Не удалось зарегистрироваться. Проверь введенные данные.";
  }
}
</script>
