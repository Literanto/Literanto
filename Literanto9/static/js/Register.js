const registerMessages = {
    emptyFields: "Todos os campos são obrigatórios",
    weakPassword: "Senha deve conter letra maiúscula, minúscula, número e caractere especial",
    passwordMismatch: "As senhas não coincidem",
    invalidEmail: "Formato de e-mail inválido",
    success: "Usuário registrado com sucesso",
    genericError: "Erro ao registrar usuário",
    serverError: "Erro ao conectar com o servidor"
};

new Vue({
    el: '#register',
    delimiters: ['[[', ']]'],

    data() {
        return {
            username: '',
            email: '',
            password: '',
            confirmPassword: '',
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

        async registerUser() {
            this.message = '';
            this.isError = false;

            this.username = this.username.trim();
            this.email = this.email.trim();

            if (!this.username || !this.email || !this.password || !this.confirmPassword) {
                this.message = registerMessages.emptyFields;
                this.isError = true;
                return;
            }

            const passwordPattern = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;

            if (!passwordPattern.test(this.password)) {
                this.message = registerMessages.weakPassword;
                this.isError = true;
                return;
            }

            if (this.password !== this.confirmPassword) {
                this.message = registerMessages.passwordMismatch;
                this.isError = true;
                return;
            }

            if (!this.email.match(/^[^\s@]+@[^\s@]+\.[^\s@]+$/)) {
                this.message = registerMessages.invalidEmail;
                this.isError = true;
                return;
            }          

            this.isLoading = true;

            try {
                const response = await axios.post('/register', {
                    username: this.username,
                    email: this.email,
                    password: this.password
                });

                if (response.data.status === 'success') {
                    this.message = registerMessages.success;
                    this.isError = false;
                    sessionStorage.setItem('registered', 'true');

                    this.username = '';
                    this.email = '';
                    this.password = '';
                    this.confirmPassword = '';                   

                    setTimeout(() => {
                        window.location.href = '/login';
                    }, 2000);

                } else {
                    this.message = registerMessages.genericError;
                    this.isError = true;
                }

            } catch (error) {
                if (error.response && error.response.data) {
                    this.message = error.response.data.error || registerMessages.genericError;
                } else {
                    this.message = registerMessages.serverError;
                }
                this.isError = true;

            } finally {
                this.isLoading = false;
            }
        }      
    },

    created() {
        if (sessionStorage.getItem('registered') === 'true') {
            sessionStorage.removeItem('registered');
            this.message = '';
            this.isError = false;
        }
    }  

});