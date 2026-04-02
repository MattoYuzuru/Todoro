<template>
  <section class="auth-panel">
    <p class="eyebrow">Вход</p>
    <h2>Вернись в рабочий поток</h2>
    <p class="lead-text">
      После входа откроется дашборд с активными задачами, live-таймерами и быстрыми действиями без лишних переходов.
    </p>

    <form class="form-grid" @submit.prevent="login">
      <div class="field-block">
        <label for="username">Username</label>
        <input id="username" v-model="username" type="text" class="field" required>
      </div>

      <div class="field-block">
        <label for="password">Password</label>
        <input id="password" v-model="password" type="password" class="field" required>
      </div>

      <div class="auth-actions">
        <button type="submit" class="button button--accent">Войти</button>
        <RouterLink class="button button--ghost" :to="{ name: 'register' }">
          Регистрация
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
import { useAuthStore } from "../store";

const authStore = useAuthStore();
const router = useRouter();

const username = ref("");
const password = ref("");
const errorMessage = ref("");

async function login() {
  try {
    const params = new URLSearchParams();
    params.append("username", username.value);
    params.append("password", password.value);

    const response = await api.post("/login", params, {
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
    });

    authStore.setToken(response.data.access_token);
    await authStore.fetchUser();
    await router.push({ name: "home" });
  } catch (error) {
    errorMessage.value = error.response?.data?.detail ?? "Неверный логин или пароль.";
  }
}
</script>
