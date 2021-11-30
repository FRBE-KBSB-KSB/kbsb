module.exports = {
  extends: ['@nuxtjs', 'plugin:nuxt/recommended'],
  rules: {
    'no-console': 'off',
    'vue/valid-v-slot': [
      'error',
      {
        allowModifiers: true
      }
    ]
  }
}
