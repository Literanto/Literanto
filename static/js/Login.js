const loginMessages = {
    emptyFields: "Preencha todos os campos",
    invalidEmail: "Formato de e-mail inválido",
    success: "Login realizado com sucesso",
    genericError: "Erro ao realizar login",
    serverError: "Erro ao conectar com o servidor"
};

new Vue({
    el: "#login",
    delimiters: ['[[', ']]'],

    data() {
        return {
            email: '',
            password: '',
            message: '',
            isError: false,
            isLoading: false
        };
    },

    methods: {
        clearMessage() {
            this.message = '';
            this.isError = false;
        },

        async login() {
            this.message = '';
            this.isError = false;

            this.email = this.email.trim();

            if (!this.email || !this.password) {
                this.message = loginMessages.emptyFields;
                this.isError = true;
                return;
            }

            if (!this.email.match(/^[^\s@]+@[^\s@]+\.[^\s@]+$/)) {
                this.message = loginMessages.invalidEmail;
                this.isError = true;
                return;
            }

            this.isLoading = true;

            try {
                const response = await axios.post('/login', {
                    email: this.email,
                    password: this.password
                });

                if (response.data.status === 'success') {
                    this.message = loginMessages.success;
                    this.isError = false;

                    this.email = '';
                    this.password = '';

                    setTimeout(() => {
                        window.location.href = response.data.redirect || '/dashboard';
                    }, 2000);
                } else {
                    this.message = response.data.message || loginMessages.genericError;
                    this.isError = true;
                }

            } catch (error) {
                if (error.response && error.response.data) {
                    this.message = error.response.data.message || loginMessages.genericError;
                } else {
                    this.message = loginMessages.serverError;
                }
                this.isError = true;

            } finally {
                this.isLoading = false;
            }
        }
    },

    created() {
        if (sessionStorage.getItem('loggedOut') === 'true') {
            sessionStorage.removeItem('loggedOut');
            this.message = '';
            this.isError = false;
        }
    }
});
