import { createRouter, createWebHistory } from "vue-router";

import AddTodo from "../components/AddTodo.vue";
import CalendarPage from "../components/CalendarPage.vue";
import DayDetail from "../components/DayDetail.vue";
import HomePage from "../components/HomePage.vue";
import TodoDetails from "../components/TodoDetails.vue";
import TodoList from "../components/TodoList.vue";
import UserAccount from "../components/UserAccount.vue";
import UserLogin from "../components/UserLogin.vue";
import UserRegister from "../components/UserRegister.vue";

const routes = [
  {
    path: "/",
    name: "home",
    component: HomePage,
  },
  {
    path: "/register",
    name: "register",
    component: UserRegister,
  },
  {
    path: "/login",
    name: "login",
    component: UserLogin,
  },
  {
    path: "/todos/create",
    name: "create-todo",
    component: AddTodo,
  },
  {
    path: "/todos/all",
    name: "todo-list",
    component: TodoList,
  },
  {
    path: "/todos/:id",
    name: "todo-details",
    component: TodoDetails,
    props: true,
  },
  {
    path: "/users/me",
    name: "user-account",
    component: UserAccount,
  },
  {
    path: "/calendar",
    name: "calendar",
    component: CalendarPage,
  },
  {
    path: "/calendar/:date",
    name: "calendar-day",
    component: DayDetail,
    props: true,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
