/**
 * Funciones JavaScript para el módulo de posts
 */

console.log('posts.js cargado correctamente');

// ============================================
// CÓDIGO QUE SE EJECUTA CUANDO EL DOM ESTÁ LISTO
// ============================================
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM cargado, inicializando posts.js');

    // ============================================
    // MANEJAR FORMULARIO DE CREAR POST
    // ============================================
    const formCreatePost = document.getElementById('formCreatePost');
    console.log('Formulario encontrado:', formCreatePost);

    if (formCreatePost) {
        formCreatePost.addEventListener('submit', function(e) {
            e.preventDefault();
            console.log('Formulario enviado!');

            const form = this;
            const formData = new FormData(form);
            const submitBtn = form.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;

            // Deshabilitar botón y mostrar loading
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Publicando...';

            console.log('Enviando a:', form.action);

            fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                }
            })
            .then(response => {
                console.log('Respuesta status:', response.status);
                return response.json();
            })
            .then(data => {
                console.log('Data recibida:', data);

                if (data.success) {
                    // Cerrar modal
                    const modalElement = document.getElementById('modalCreatePost');
                    const modal = bootstrap.Modal.getInstance(modalElement);
                    if (modal) {
                        modal.hide();
                    }

                    // Limpiar formulario
                    form.reset();
                    const previewMedia = document.getElementById('previewMedia');
                    if (previewMedia) {
                        previewMedia.innerHTML = '';
                    }

                    // Mostrar mensaje de éxito
                    showToast('Publicación creada exitosamente', 'success');

                    // Recargar página después de 500ms
                    console.log('Recargando página...');
                    setTimeout(() => {
                        window.location.reload();
                    }, 500);
                } else {
                    console.error('Error en respuesta:', data);
                    showToast(data.error || 'Error al crear publicación', 'danger');
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = originalText;
                }
            })
            .catch(error => {
                console.error('Error en fetch:', error);
                showToast('Error al crear publicación', 'danger');
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalText;
            });
        });
    } else {
        console.error('NO SE ENCONTRÓ #formCreatePost');
    }

    // ============================================
    // PREVIEW DE IMÁGENES
    // ============================================
    const imageInput = document.querySelector('input[name="images"]');
    if (imageInput) {
        imageInput.addEventListener('change', function(e) {
            const preview = document.getElementById('previewMedia');
            if (!preview) return;

            preview.innerHTML = '';

            Array.from(e.target.files).forEach((file, index) => {
                if (file.type.startsWith('image/')) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        const div = document.createElement('div');
                        div.className = 'position-relative d-inline-block me-2 mb-2';
                        div.innerHTML = `
                            <img src="${e.target.result}" class="img-thumbnail" style="max-height: 150px; max-width: 150px;">
                            <button type="button" class="btn btn-sm btn-danger position-absolute top-0 end-0" onclick="this.parentElement.remove()">
                                <i class="bi bi-x"></i>
                            </button>
                        `;
                        preview.appendChild(div);
                    }
                    reader.readAsDataURL(file);
                }
            });
        });
    }

    // ============================================
    // PREVIEW DE VIDEOS
    // ============================================
    const videoInput = document.querySelector('input[name="videos"]');
    if (videoInput) {
        videoInput.addEventListener('change', function(e) {
            const preview = document.getElementById('previewMedia');
            if (!preview) return;

            Array.from(e.target.files).forEach((file, index) => {
                if (file.type.startsWith('video/')) {
                    const div = document.createElement('div');
                    div.className = 'position-relative d-inline-block me-2 mb-2';
                    div.innerHTML = `
                        <video class="img-thumbnail" style="max-height: 150px; max-width: 150px;" controls>
                            <source src="${URL.createObjectURL(file)}" type="${file.type}">
                        </video>
                        <button type="button" class="btn btn-sm btn-danger position-absolute top-0 end-0" onclick="this.parentElement.remove()">
                            <i class="bi bi-x"></i>
                        </button>
                    `;
                    preview.appendChild(div);
                }
            });
        });
    }

    console.log('posts.js inicializado correctamente');
});

// ============================================
// FUNCIONES GLOBALES (fuera de DOMContentLoaded)
// ============================================

// Fijar/Desfijar post
function pinPost(postId) {
    fetch(`/posts/${postId}/pin/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            alert('Error al fijar la publicación');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error al procesar la solicitud');
    });
}

// Archivar post
function archivePost(postId) {
    if (confirm('¿Estás seguro de archivar esta publicación?')) {
        fetch(`/posts/${postId}/archive/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.querySelector(`[data-post-id="${postId}"]`).remove();
                showToast('Publicación archivada exitosamente', 'success');
            } else {
                alert('Error al archivar la publicación');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error al procesar la solicitud');
        });
    }
}

// Toggle like en post
function toggleLike(postId) {
    fetch(`/likes/post/${postId}/toggle/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

// Eliminar imagen de post
function deletePostImage(imageId, postId) {
    if (confirm('¿Estás seguro de eliminar esta imagen?')) {
        fetch(`/posts/image/${imageId}/delete/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                alert('Error al eliminar la imagen');
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }
}

// Eliminar video de post
function deletePostVideo(videoId, postId) {
    if (confirm('¿Estás seguro de eliminar este video?')) {
        fetch(`/posts/video/${videoId}/delete/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                alert('Error al eliminar el video');
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }
}

// Función auxiliar para obtener el CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Toast notification
function showToast(message, type = 'info') {
    const toastHTML = `
        <div class="toast align-items-center text-white bg-${type} border-0" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;

    const toastContainer = document.getElementById('toastContainer');
    if (toastContainer) {
        toastContainer.insertAdjacentHTML('beforeend', toastHTML);
        const toastElement = toastContainer.lastElementChild;
        const toast = new bootstrap.Toast(toastElement, { delay: 3000 });
        toast.show();

        toastElement.addEventListener('hidden.bs.toast', () => {
            toastElement.remove();
        });
    } else {
        console.warn('toastContainer no encontrado');
        alert(message);
    }
}

// Cargar más posts
function loadMorePosts() {
    console.log('Cargando más posts...');
}
