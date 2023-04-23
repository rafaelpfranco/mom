$(document).ready(function() {
    $('#message').submit(function(event) {
      // Previne o comportamento padrão do formulário (atualizar a página)
      event.preventDefault();
      
      // Obtém os dados do formulário
      var formData = $(this).serialize();
      
      // Envia os dados para o servidor usando AJAX
      $.ajax({
        url: 'seu-arquivo-de-processamento.php',
        method: 'POST',
        data: formData,
        success: function(response) {
          // Faz algo com a resposta do servidor, se necessário
          alert(response);
        }
      });
    });
  });