document.addEventListener('DOMContentLoaded', function() {
    new Vue({
        el: "#dashboard",  // <- corrigido aqui
        delimiters: ["[[", "]]"],
        data: {
            username: "",
            currentPage: "myStories",
            arroba: "",
            isSidebarCollapsed: false,
            abaSelecionada: 'publicado'
        },

        methods: {
            setPage(page) {
                this.currentPage = page;
            },

            toggleSidebar() {
                this.isSidebarCollapsed = !this.isSidebarCollapsed;
            },

            logout() {
                axios.post('/logout')
                    .then(response => {
                        if (response.data.redirect) {
                            window.location.href = response.data.redirect;
                        }
                    })
                    .catch(error => {
                        console.error("Erro ao fazer logout:", error);
                        window.location.href = '/login';
                    });
            },

            checkSession() {
                axios.get('/check_session')
                    .then(response => {
                        if (!response.data.logged_in) {
                            window.location.href = "/login";
                        } else {
                            this.arroba = response.data.arroba;
                            this.username = response.data.username;
                        }
                    })
                    .catch(() => {
                        window.location.href = "/login";
                    });
            },

            criarNovaHistoria() {
                window.location.href = "/story";
            }
        },

        created() {
            this.checkSession();
        }
    });
});
