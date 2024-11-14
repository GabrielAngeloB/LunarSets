document.addEventListener('DOMContentLoaded', function() {
    const Toast = Swal.mixin({
        toast: true,
        position: 'top-end',
        iconColor: 'white',
        showConfirmButton: false,
        timer: 1500,
        timerProgressBar: true,
    });

    function getToastClass(category) {
        const classes = {
            success: 'swal2-toast-success',
            danger: 'swal2-toast-danger',
            error: 'swal2-toast-error',
            warning: 'swal2-toast-warning',
            info: 'swal2-toast-info'
        };
        return classes[category] || 'swal2-toast-info';
    }
});

document.addEventListener('DOMContentLoaded', function() {
    const resultsContainer = document.querySelector('.results-container');
    if (resultsContainer) {
        setTimeout(() => {
            resultsContainer.classList.add('visible');
        }, 100);
    }
});
// Função para alternar para o modo de edição
function enableEditMode(id) {
    // Esconde o texto do comentário e exibe o campo de entrada
    document.getElementById(`text-${id}`).style.display = 'none';
    document.getElementById(`input-${id}`).style.display = 'block';
    
    // Exibe o botão de salvar e oculta o botão de editar
    document.querySelector(`#comment-${id} .btn-edit`).style.display = 'none';
    document.getElementById(`save-${id}`).style.display = 'inline';
    }
    
    function saveEdit(commentId) {
    const newText = document.getElementById(`input-${commentId}`).value;
    const next = window.location.pathname;  // Captura a página atual
    
    Swal.fire({
        title: "Tem certeza?",
        text: "Você está prestes a salvar suas alterações.",
        icon: "warning",
        showCancelButton: true,
        confirmButtonColor: "#67c29c",
        cancelButtonColor: "#d33",
        confirmButtonText: "Sim, salvar!",
        cancelButtonText: "Cancelar"
    }).then((result) => {
        if (result.isConfirmed) {
            // Cria um formulário para enviar o novo texto
            const form = document.createElement('form');
            form.method = 'POST';
            
            // Define a ação do formulário com o `next`
            form.action = `/editar_comentario/${commentId}?next=${next}`;
            
            // Adiciona o campo com o novo texto ao formulário
            const input = document.createElement('input');
            input.type = 'hidden';
            input.name = 'novo_texto';
            input.value = newText;
            form.appendChild(input);
            
            document.body.appendChild(form);
            form.submit();
        }
    });
    }
    
    function deletarComentario(event, commentId) {
    // Impede o comportamento padrão do botão
    event.preventDefault();
    const next = window.location.pathname;  // Captura o caminho atual da página
    
    Swal.fire({
        title: "Tem certeza?",
        text: "Você está prestes a excluir seu comentário!",
        icon: "warning",
        showCancelButton: true,
        confirmButtonColor: "#67c29c",
        cancelButtonColor: "#d33",
        confirmButtonText: "Sim, excluir!",
        cancelButtonText: "Cancelar"
    }).then((result) => {
        if (result.isConfirmed) {
            // Cria um formulário para enviar o pedido de exclusão
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = `/deletar_comentario/${commentId}?next=${next}`;  // Inclui o `next`
            
            document.body.appendChild(form);
            form.submit();
        }
    });
    }
    document.addEventListener("keydown", function(event) {
        if (event.key === "F5") {
            event.preventDefault(); // Evita o comportamento padrão do F5
            location.reload(true);   // Recarrega a página com `location.reload(true)`
        }
    });

    