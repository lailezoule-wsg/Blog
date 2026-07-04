import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '../stores/user'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      component: () => import('../layouts/MainLayout.vue'),
      children: [
        {
          path: '',
          name: 'Home',
          component: () => import('../views/Home.vue'),
        },
        {
          path: 'article/:id',
          name: 'ArticleDetail',
          component: () => import('../views/article/Detail.vue'),
        },
        {
          path: 'article/write',
          name: 'ArticleWrite',
          component: () => import('../views/article/Edit.vue'),
          meta: { requiresAuth: true },
        },
        {
          path: 'article/edit/:id',
          name: 'ArticleEdit',
          component: () => import('../views/article/Edit.vue'),
          meta: { requiresAuth: true },
        },
        {
          path: 'user/profile',
          name: 'UserProfile',
          component: () => import('../views/user/Profile.vue'),
          meta: { requiresAuth: true },
        },
        {
          path: 'user/articles',
          name: 'MyArticles',
          component: () => import('../views/user/MyArticles.vue'),
          meta: { requiresAuth: true },
        },
        {
          path: 'admin/categories',
          name: 'AdminCategories',
          component: () => import('../views/admin/Categories.vue'),
          meta: { requiresAuth: true, requiresAdmin: true },
        },
        {
          path: 'admin/tags',
          name: 'AdminTags',
          component: () => import('../views/admin/Tags.vue'),
          meta: { requiresAuth: true, requiresAdmin: true },
        },
      ],
    },
    {
      path: '/login',
      name: 'Login',
      component: () => import('../views/user/Login.vue'),
    },
    {
      path: '/register',
      name: 'Register',
      component: () => import('../views/user/Register.vue'),
    },
  ],
})

router.beforeEach(async (to, from, next) => {
  const userStore = useUserStore()

  if (userStore.isLoggedIn && !userStore.user) {
    await userStore.fetchCurrentUser()
  }

  if (to.meta.requiresAuth && !userStore.isLoggedIn) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
  } else if (to.meta.requiresAdmin && !userStore.isAdmin) {
    next({ name: 'Home' })
  } else {
    next()
  }
})

export default router
