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
            arroba: '',
            username: '',
            email: '',
            password: '',
            confirmPassword: '',
            date_of_birth: '',
            message: '',
            isError: false,
            isLoading: false,
            maxDate: new Date().toISOString().split('T')[0],
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

            if (!this.username || !this.email || !this.password || !this.confirmPassword || 
                !this.arroba || !this.date_of_birth) {
                this.message = registerMessages.emptyFields;
                this.isError = true;
                return;
            }            
        
            if (!/^[a-zA-Z0-9_]+$/.test(this.arroba)) {
                this.message = 'O arroba deve conter apenas letras, números e underline.';
                this.isError = true;
                return;
            }

            const passwordPattern = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;

            if (!passwordPattern.test(this.password)) {
                this.message = registerMessages.weakPassword;
                this.isError = true;
                return;
            }

            const selectedDate = new Date(this.date_of_birth);
            const today = new Date();

            if (selectedDate > today) {
                this.message = "Data de nascimento não pode ser no futuro.";
                this.isError = true;
                return;
            }

            let age = today.getFullYear() - selectedDate.getFullYear();
            const month = today.getMonth();
            
            if (month < selectedDate.getMonth() || (month === selectedDate.getMonth() && today.getDate() < selectedDate.getDate())) {
                age--;
            }

            if (age < 13) {
                this.message = "Você precisa ter pelo menos 13 anos para se registrar.";
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
                    arroba: this.arroba,
                    username: this.username,
                    email: this.email,
                    password: this.password,
                    date_of_birth: this.date_of_birth
                });
                

                if (response.data.status === 'success') {
                    this.message = registerMessages.success;
                    this.isError = false;
                    sessionStorage.setItem('registered', 'true');

                    this.username = '';
                    this.email = '';
                    this.password = '';
                    this.confirmPassword = '';
                    this.arroba = '';
                    this.date_of_birth = '';
              

                    setTimeout(() => {
                        window.location.href = '/login';
                    }, 2000);

                } else {
                    this.message = registerMessages.genericError;
                    this.isError = true;
                }

            } catch (error) {
                if (error.response && error.response.data) {
                    this.message = error.response.data.message || registerMessages.genericError;
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
            this.message = registerMessages.success;
            this.isError = false;
        }
    }  

});