/**
 * Sistema de Likes para UnicoNet
 * Maneja todas las interacciones de likes mediante AJAX
 */

class LikeManager {
    constructor() {
        this.initEventListeners();
        this.csrfToken = this.getCsrfToken();
    }

    /**
     * Obtiene el CSRF token de Django
     */
    getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
               document.querySelector('meta[name="csrf-token"]')?.content ||
               this.getCookie('csrftoken');
    }

    /**
     * Obtiene una cookie por nombre
     */
    getCookie(name) {
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

    /**
     * Inicializa los event listeners
     */
    initEventListeners() {
        // Delegar eventos de like a nivel de documento
        document.addEventListener('click', (e) => {
            // Botón de like/unlike
            if (e.target.closest('[data-action="toggle-like"]')) {
                e.preventDefault();
                const button = e.target.closest('[data-action="toggle-like"]');
                this.toggleLike(button);
            }

            // Ver lista de likes
            if (e.target.closest('[data-action="view-likes"]')) {
                e.preventDefault();
                const button = e.target.closest('[data-action="view-likes"]');
                const postId = button.dataset.postId;
                this.showLikesModal(postId);
            }
        });
    }

    /**
     * Alterna el like de un post
     */
    async toggleLike(button) {
        const postId = button.dataset.postId;
        const postCard = button.closest('.post-card');
        
        // Prevenir clicks múltiples
        if (button.disabled) return;
        button.disabled = true;

        try {
            const response = await fetch(`/likes/toggle/${postId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.csrfToken,
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/json'
                }
            });

            const data = await response.json();

            if (data.success) {
                this.updateLikeButton(button, data.liked, data.likes_count);
                this.showToast(data.message, 'success');
                
                // Animación del botón
                this.animateLike(button, data.liked);
            } else {
                this.showToast(data.error || 'Error al procesar el like', 'error');
            }

        } catch (error) {
            console.error('Error en toggleLike:', error);
            this.showToast('Error de conexión', 'error');
        } finally {
            button.disabled = false;
        }
    }

    /**
     * Actualiza el estado visual del botón de like
     */
    updateLikeButton(button, liked, likesCount) {
        const icon = button.querySelector('i');
        const countSpan = button.querySelector('.likes-count');
        
        // Actualizar icono
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
        if (countSpan) {
            countSpan.textContent = likesCount;
            
            // Ocultar si no hay likes
            const likesContainer = button.closest('.post-actions')?.querySelector('.likes-info');
            if (likesContainer) {
                likesContainer.style.display = likesCount > 0 ? 'flex' : 'none';
            }
        }

        // Actualizar aria-label para accesibilidad
        button.setAttribute('aria-label', liked ? 'Quitar me gusta' : 'Me gusta');
    }

    /**
     * Animación al dar/quitar like
     */
    animateLike(button, liked) {
        const icon = button.querySelector('i');
        
        if (liked) {
            // Animación de "pop" al dar like
            icon.style.transform = 'scale(1.3)';
            setTimeout(() => {
                icon.style.transform = 'scale(1)';
            }, 200);
            
            // Efecto de corazones flotantes (opcional)
            this.createHeartParticle(button);
        }
    }

    /**
     * Crea partícula de corazón flotante (efecto visual)
     */
    createHeartParticle(button) {
        const heart = document.createElement('i');
        heart.className = 'bi bi-heart-fill position-absolute text-danger';
        heart.style.cssText = `
            font-size: 1.5rem;
            opacity: 1;
            pointer-events: none;
            animation: floatHeart 1s ease-out forwards;
        `;
        
        const rect = button.getBoundingClientRect();
        heart.style.left = `${rect.left + rect.width / 2}px`;
        heart.style.top = `${rect.top}px`;
        
        document.body.appendChild(heart);
        
        setTimeout(() => heart.remove(), 1000);
    }

    /**
     * Muestra modal con lista de usuarios que dieron like
     */
    async showLikesModal(postId) {
        try {
            const response = await fetch(`/likes/post/${postId}/preview/`, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            const data = await response.json();

            if (data.error) {
                this.showToast(data.error, 'error');
                return;
            }

            this.renderLikesModal(data, postId);

        } catch (error) {
            console.error('Error al cargar likes:', error);
            this.showToast('Error al cargar la lista de likes', 'error');
        }
    }

    /**
     * Renderiza el modal de likes
     */
    renderLikesModal(data, postId) {
        // Crear o actualizar modal
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
                                <i class="bi bi-heart-fill text-danger"></i>
                                Me gusta
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body" id="likesModalBody">
                            <!-- Content here -->
                        </div>
                        <div class="modal-footer">
                            <a href="/likes/post/${postId}/" class="btn btn-sm btn-outline-primary">
                                Ver todos (${data.total_count})
                            </a>
                        </div>
                    </div>
                </div>
            `;
            document.body.appendChild(modal);
        }

        // Actualizar contenido
        const modalBody = document.getElementById('likesModalBody');
        
        if (data.likers.length === 0) {
            modalBody.innerHTML = `
                <div class="text-center py-4 text-muted">
                    <i class="bi bi-heart" style="font-size: 3rem;"></i>
                    <p class="mt-2">Todavía no hay likes en esta publicación</p>
                </div>
            `;
        } else {
            modalBody.innerHTML = data.likers.map(user => `
                <div class="d-flex align-items-center mb-3 p-2 rounded hover-bg">
                    <img src="https://ui-avatars.com/api/?name=${encodeURIComponent(user.full_name)}&background=0d47a1&color=fff" 
                         class="rounded-circle me-3" 
                         width="40" 
                         height="40" 
                         alt="${user.full_name}">
                    <div class="flex-grow-1">
                        <a href="${user.profile_url}" class="text-decoration-none">
                            <strong>${user.full_name}</strong>
                        </a>
                        <div class="small text-muted">@${user.username}</div>
                    </div>
                </div>
            `).join('');

            // Si hay más likes
            if (data.has_more) {
                modalBody.innerHTML += `
                    <div class="text-center mt-3">
                        <a href="/likes/post/${postId}/" class="btn btn-sm btn-outline-primary">
                            Ver todos los ${data.total_count} likes
                        </a>
                    </div>
                `;
            }
        }

        // Mostrar modal
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
    }

    /**
     * Muestra toast notification
     */
    showToast(message, type = 'info') {
        const toastContainer = document.getElementById('toastContainer') || this.createToastContainer();
        
        const toastId = 'toast-' + Date.now();
        const bgClass = {
            'success': 'bg-success',
            'error': 'bg-danger',
            'info': 'bg-info',
            'warning': 'bg-warning'
        }[type] || 'bg-info';

        const toastHTML = `
            <div id="${toastId}" class="toast align-items-center text-white ${bgClass} border-0" role="alert">
                <div class="d-flex">
                    <div class="toast-body">
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            </div>
        `;

        toastContainer.insertAdjacentHTML('beforeend', toastHTML);
        
        const toastElement = document.getElementById(toastId);
        const toast = new bootstrap.Toast(toastElement, {
            autohide: true,
            delay: 3000
        });
        
        toast.show();

        // Remover del DOM después de ocultar
        toastElement.addEventListener('hidden.bs.toast', () => {
            toastElement.remove();
        });
    }

    /**
     * Crea el contenedor de toasts si no existe
     */
    createToastContainer() {
        const container = document.createElement('div');
        container.id = 'toastContainer';
        container.className = 'position-fixed bottom-0 end-0 p-3';
        container.style.zIndex = '11';
        document.body.appendChild(container);
        return container;
    }
}

// CSS para animaciones
const style = document.createElement('style');
style.textContent = `
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
    }
    
    [data-action="toggle-like"] {
        transition: all 0.2s ease;
    }
    
    [data-action="toggle-like"] i {
        transition: transform 0.2s ease;
    }
    
    [data-action="toggle-like"]:hover i {
        transform: scale(1.1);
    }
`;
document.head.appendChild(style);

// Inicializar cuando el DOM esté listo
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.likeManager = new LikeManager();
    });
} else {
    window.likeManager = new LikeManager();
}