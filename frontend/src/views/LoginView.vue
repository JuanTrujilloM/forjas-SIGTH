<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import forjasLogo from '@/assets/images/forjas-logo.svg'
import loginHero from '@/assets/images/login-hero.webp'
import BaseService from '@/shared/services/BaseService'
import { useSessionStore } from '@/stores/session'

const CORPORATE_DOMAIN: string = import.meta.env.VITE_CORPORATE_EMAIL_DOMAIN

const route = useRoute()
const router = useRouter()
const session = useSessionStore()

const email = ref('')
const password = ref('')
const isPasswordVisible = ref(false)
const isLoading = ref(false)
const errorMessage = ref<string | null>(null)
const wasSubmitted = ref(false)

// Convenience for whoever is typing; the domain that decides is the one the backend
// validates on the model field and on the login serializer (3.3).
const emailError = computed<string | null>(() => {
  if (!email.value.trim()) {
    return 'Escribe tu correo corporativo.'
  }

  if (!email.value.trim().toLowerCase().endsWith(`@${CORPORATE_DOMAIN.toLowerCase()}`)) {
    return `El correo debe pertenecer al dominio @${CORPORATE_DOMAIN}.`
  }

  return null
})

const passwordError = computed<string | null>(() =>
  password.value ? null : 'Escribe tu contraseña.',
)

async function submit(): Promise<void> {
  wasSubmitted.value = true
  errorMessage.value = null

  if (emailError.value || passwordError.value) {
    return
  }

  isLoading.value = true

  try {
    await session.login({ email: email.value.trim(), password: password.value })

    const destination = route.query.destino
    await router.replace(typeof destination === 'string' ? destination : { name: 'home' })
  } catch (error) {
    errorMessage.value = BaseService.getApiErrorMessage(error, 'No se pudo iniciar sesión.')
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <!-- align-content-start keeps the stacked mobile layout from spreading the leftover
       height over the logo band; from lg up the two panels share one line again -->
  <main class="row g-0 min-vh-100 align-content-start align-content-lg-stretch">
    <section class="col-12 col-lg-6 login-hero">
      <img class="login-hero__photo" :src="loginHero" alt="" aria-hidden="true" />

      <div class="login-hero__content">
        <img class="login-hero__logo" :src="forjasLogo" alt="Forjas Bolívar" />

        <p class="login-hero__tagline d-none d-lg-block">
          Sistema de Información y Gestión de Talento Humano
        </p>
      </div>
    </section>

    <section class="col-12 col-lg-6 d-flex flex-column justify-content-center login-panel">
      <div class="login-form">
        <h1 class="h3 fw-semibold mb-1">Ingreso al SIGTH</h1>

        <p class="text-secondary mb-4">Entra con tu correo corporativo.</p>

        <div v-if="errorMessage" class="alert alert-danger" role="alert">
          {{ errorMessage }}
        </div>

        <form novalidate @submit.prevent="submit">
          <div class="mb-3">
            <label class="form-label" for="email">Correo corporativo</label>

            <input
              id="email"
              v-model="email"
              class="form-control"
              :class="{ 'is-invalid': wasSubmitted && emailError }"
              type="email"
              autocomplete="username"
              :placeholder="`ejemplo@${CORPORATE_DOMAIN}`"
              :disabled="isLoading"
              required
            />

            <div v-if="wasSubmitted && emailError" class="invalid-feedback">{{ emailError }}</div>
          </div>

          <div class="mb-4">
            <label class="form-label" for="password">Contraseña</label>

            <div class="input-group has-validation">
              <input
                id="password"
                v-model="password"
                class="form-control"
                :class="{ 'is-invalid': wasSubmitted && passwordError }"
                :type="isPasswordVisible ? 'text' : 'password'"
                autocomplete="current-password"
                :disabled="isLoading"
                required
              />

              <button
                class="btn btn-outline-secondary"
                type="button"
                :disabled="isLoading"
                :aria-pressed="isPasswordVisible"
                @click="isPasswordVisible = !isPasswordVisible"
              >
                {{ isPasswordVisible ? 'Ocultar' : 'Mostrar' }}
              </button>

              <div v-if="wasSubmitted && passwordError" class="invalid-feedback">
                {{ passwordError }}
              </div>
            </div>
          </div>

          <button class="btn btn-accent w-100 fw-semibold py-2" type="submit" :disabled="isLoading">
            <span
              v-if="isLoading"
              class="spinner-border spinner-border-sm me-2"
              aria-hidden="true"
            />
            {{ isLoading ? 'Ingresando…' : 'Ingresar' }}
          </button>

          <p v-if="isLoading" class="visually-hidden" role="status">Verificando tus datos.</p>
        </form>

        <p class="text-secondary small mt-4 mb-0">
          ¿Olvidaste tu contraseña? Comunícate con Recursos Humanos o con el área de TI para que la
          restablezcan.
        </p>
      </div>
    </section>
  </main>
</template>

<style scoped>
/* main code */
/* One block, two sizes: a banner over the form on a phone, the left half of the split
   from lg up. Two markup branches would mean maintaining the same hero twice. */
.login-hero {
  position: relative;
  overflow: hidden;
  background-color: var(--fb-blue-darker);
  height: 13rem;
}

@media (min-width: 992px) {
  .login-hero {
    height: auto;
  }
}

.login-hero__photo {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  /* the panel is a tall crop of a landscape photo; centring it would cut the worker in half */
  object-position: 68% center;
}

/* Darkest where the logo and the tagline sit and almost clear in between, so the wash
   buys contrast for the text without flattening the photograph. */
.login-hero::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(
    180deg,
    rgba(0, 22, 49, 0.62) 0%,
    rgba(0, 32, 73, 0.18) 38%,
    rgba(0, 32, 73, 0.32) 62%,
    rgba(0, 22, 49, 0.88) 100%
  );
}

.login-hero__content {
  position: relative;
  z-index: 1;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 1.75rem;
}

@media (min-width: 992px) {
  .login-hero__content {
    padding: 3rem;
  }
}

.login-hero__logo {
  width: 150px;
  max-width: 60%;
}

@media (min-width: 992px) {
  .login-hero__logo {
    width: 200px;
  }
}

.login-hero__tagline {
  margin: 0;
  max-width: 24ch;
  color: #fff;
  font-size: 1.75rem;
  font-weight: 500;
  line-height: 1.3;
}

.login-panel {
  background-color: #fff;
}

.login-form {
  width: 100%;
  max-width: 24rem;
  margin: 0 auto;
  padding: 3rem 1.5rem;
}
</style>
