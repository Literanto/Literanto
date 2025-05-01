new Vue({
    el: '#dashboard',
    data: {
        currentPage "story",
      story: {
        titulo: '',
        descricao: '',
        conteudo: '',
        previewCapa: ''
      },
      novaHistoria: {},
      isSidebarCollapsed: false
    },
    methods: {
      carregarCapa(event) {
        const file = event.target.files[0];
        if (file) {
          this.story.previewCapa = URL.createObjectURL(file);
        }
      },
      salvarHistoria() {
        console.log("Publicar história:", this.story);
      },
      salvarComoRascunho() {
        console.log("Salvar como rascunho:", this.story);
      },
      toggleSidebar() {
        this.isSidebarCollapsed = !this.isSidebarCollapsed;
      }
    }
  });
  