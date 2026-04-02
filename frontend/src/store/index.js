import { computed, ref } from "vue";
import { defineStore } from "pinia";

import api from "../api/client";

export const useAuthStore = defineStore("auth", () => {
  const user = ref(null);
  const token = ref(localStorage.getItem("token"));

  const isAuthenticated = computed(() => Boolean(token.value));

  async function fetchUser() {
    if (!token.value) {
      user.value = null;
      return null;
    }

    try {
      const response = await api.get("/users/me/");
      user.value = response.data;
      return user.value;
    } catch (error) {
      console.error("Не удалось получить профиль пользователя:", error);
      logout();
      return null;
    }
  }

  function setToken(value) {
    token.value = value;
    localStorage.setItem("token", value);
  }

  function logout() {
    token.value = null;
    user.value = null;
    localStorage.removeItem("token");
  }

  return {
    fetchUser,
    isAuthenticated,
    logout,
    setToken,
    token,
    user,
  };
});
