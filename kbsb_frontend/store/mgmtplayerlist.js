
export const state = () => ({
    step: 1,
})

export const mutations = {
    restart(state) {
        state.step = 1
    },
    updateStep(state, value) {
        state.step = value
    }
}
