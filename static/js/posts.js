/**
 * Funciones JavaScript para el módulo de posts
 * Incluye sistema completo de likes integrado
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
                            <img src="${e.target.result}" class="img-thumbnail" style="max-height: 150px; max-width: 150px; object-fit: cover;">
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
// EVENT LISTENERS GLOBALES (FUERA DE DOMContentLoaded)
// ============================================

// Event listener para clicks en botones de like y ver likes
document.addEventListener('click', function(e) {
    // Click en botón de like
    const likeButton = e.target.closest('[data-action="toggle-like"]');
    if (likeButton) {
        e.preventDefault();
        const postId = likeButton.dataset.postId;
        console.log('Click en like, Post ID:', postId);
        toggleLike(postId);
    }
    
    // Click para ver lista de likes
    const viewLikesButton = e.target.closest('[data-action="view-likes"]');
    if (viewLikesButton) {
        e.preventDefault();
        const postId = viewLikesButton.dataset.postId;
        showLikesModal(postId);
    }
});

// ============================================
// FUNCIONES GLOBALES - POSTS
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
            showToast(data.is_pinned ? 'Publicación fijada' : 'Publicación desfijada', 'success');
            setTimeout(() => location.reload(), 500);
        } else {
            showToast('Error al fijar la publicación', 'danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('Error al procesar la solicitud', 'danger');
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
                showToast('Error al archivar la publicación', 'danger');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('Error al procesar la solicitud', 'danger');
        });
    }
}

// ============================================
// SISTEMA DE LIKES
// ============================================

// Toggle like en post
function toggleLike(postId) {
    const button = document.querySelector(`[data-action="toggle-like"][data-post-id="${postId}"]`);
    if (!button) {
        console.error('Botón de like no encontrado para post:', postId);
        return;
    }

    // Prevenir clicks múltiples
    if (button.disabled) return;
    button.disabled = true;

    fetch(`/likes/toggle/${postId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        console.log('Respuesta del servidor:', data);
        if (data.success) {
            // Actualizar UI
            updateLikeButton(button, data.liked, data.likes_count);
            
            // Animación
            if (data.liked) {
                animateLikeButton(button);
            }
            
            showToast(data.message, 'success');
        } else {
            showToast(data.error || 'Error al procesar el like', 'danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('Error de conexión', 'danger');
    })
    .finally(() => {
        button.disabled = false;
    });
}

// Actualizar botón de like
function updateLikeButton(button, liked, likesCount) {
    const icon = button.querySelector('i');
    const postCard = button.closest('.post-card');
    const likesInfo = postCard.querySelector('.likes-info');
    const likesCountSpan = postCard.querySelector('.likes-count');
    
    // Actualizar icono y color
    if (liked) {
        icon.classList.remove('bi-heart');
        icon.classList.add('bi-heart-fill');
        button.classList.add('text-danger');
        button.classList.remove('text-muted');
    } else {
        icon.classList.remove('bi-heart-fill');
        icon.classList.add('bi-heart');
        button.classList.remove('text-danger');
        button.classList.add('text-muted');
    }
    
    // Actualizar contador
    if (likesCountSpan) {
        likesCountSpan.textContent = likesCount;
    }
    
    // Mostrar/ocultar sección de likes
    if (likesInfo) {
        likesInfo.style.display = likesCount > 0 ? 'flex' : 'none';
    }
}

// Animación del botón de like
function animateLikeButton(button) {
    const icon = button.querySelector('i');
    icon.style.transition = 'transform 0.2s ease';
    icon.style.transform = 'scale(1.3)';
    setTimeout(() => {
        icon.style.transform = 'scale(1)';
    }, 200);
    createFloatingHeart(button);
}

// Crear corazón flotante
function createFloatingHeart(button) {
    const heart = document.createElement('i');
    heart.className = 'bi bi-heart-fill text-danger position-fixed';
    heart.style.cssText = `
        font-size: 1.5rem;
        opacity: 1;
        pointer-events: none;
        z-index: 9999;
        animation: floatHeart 1s ease-out forwards;
    `;
    const rect = button.getBoundingClientRect();
    heart.style.left = `${rect.left + rect.width / 2 - 12}px`;
    heart.style.top = `${rect.top - 10}px`;
    document.body.appendChild(heart);
    setTimeout(() => heart.remove(), 1000);
}

// Mostrar modal de likes
function showLikesModal(postId) {
    fetch(`/likes/post/${postId}/preview/`, {
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            showToast(data.error, 'danger');
            return;
        }
        renderLikesModal(data, postId);
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('Error al cargar likes', 'danger');
    });
}

// Renderizar modal de likes
function renderLikesModal(data, postId) {
    let modal = document.getElementById('likesModal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'likesModal';
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog modal-dialog-scrollable">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">
                            <i class="bi bi-heart-fill text-danger"></i> Me gusta
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body" id="likesModalBody"></div>
                    <div class="modal-footer" id="likesModalFooter"></div>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
    }
    
    const modalBody = document.getElementById('likesModalBody');
    const modalFooter = document.getElementById('likesModalFooter');
    
    if (data.likers.length === 0) {
        modalBody.innerHTML = `
            <div class="text-center py-5 text-muted">
                <i class="bi bi-heart" style="font-size: 3rem;"></i>
                <p class="mt-3 mb-0">Sé el primero en dar like</p>
            </div>
        `;
        modalFooter.innerHTML = '';
    } else {
        modalBody.innerHTML = data.likers.map(user => `
            <div class="d-flex align-items-center mb-3 p-2 rounded hover-bg">
                <img src="https://ui-avatars.com/api/?name=${encodeURIComponent(user.full_name)}&background=0d47a1&color=fff" 
                     class="rounded-circle me-3" width="40" height="40" alt="${user.full_name}">
                <div class="flex-grow-1">
                    <a href="${user.profile_url}" class="text-decoration-none text-dark">
                        <strong>${user.full_name}</strong>
                    </a>
                    <div class="small text-muted">@${user.username}</div>
                </div>
            </div>
        `).join('');
        
        modalFooter.innerHTML = data.has_more ? 
            `<a href="/likes/post/${postId}/" class="btn btn-primary">Ver todos (${data.total_count})</a>` : '';
    }
    
    new bootstrap.Modal(modal).show();
}

// ============================================
// FUNCIONES AUXILIARES
// ============================================

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

    let toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toastContainer';
        toastContainer.className = 'position-fixed bottom-0 end-0 p-3';
        toastContainer.style.zIndex = '11';
        document.body.appendChild(toastContainer);
    }

    toastContainer.insertAdjacentHTML('beforeend', toastHTML);
    const toastElement = toastContainer.lastElementChild;
    const toast = new bootstrap.Toast(toastElement, { delay: 3000 });
    toast.show();

    toastElement.addEventListener('hidden.bs.toast', () => {
        toastElement.remove();
    });
}

// Cargar más posts
function loadMorePosts() {
    console.log('Cargando más posts...');
    showToast('Funcionalidad en desarrollo', 'info');
}

// ============================================
// CSS DINÁMICO PARA LIKES
// ============================================
const likesStyle = document.createElement('style');
likesStyle.textContent = `
    @keyframes floatHeart {
        0% {
            transform: translateY(0) scale(1);
            opacity: 1;
        }
        100% {
            transform: translateY(-50px) scale(0.5);
            opacity: 0;
        }
    }
    
    .hover-bg:hover {
        background-color: #f0f2f5;
        cursor: pointer;
    }
    
    [data-action="toggle-like"] {
        transition: all 0.2s ease;
        cursor: pointer;
    }
    
    [data-action="toggle-like"]:hover {
        background-color: #fee !important;
    }
    
    [data-action="toggle-like"].text-danger:hover {
        background-color: #ffe0e0 !important;
    }
    
    [data-action="view-likes"]:hover {
        text-decoration: underline !important;
    }
    
    [data-action="view-likes"] {
        transition: opacity 0.2s;
    }
    
    [data-action="view-likes"]:hover {
        opacity: 0.8;
    }
`;
document.head.appendChild(likesStyle);

console.log('✅ Sistema de likes completamente cargado');