// Shared Rating Modal Logic
// This file should be included in both question and question_task_list templates
// It expects the following HTML structure for the modal:
// <div id="rating-modal">...</div>
//
// Usage: window.RatingModal.init({
//   modalId: 'rating-modal',
//   starsId: 'modal-stars',
//   messageId: 'modal-message',
//   submitBtnId: 'modal-submit-btn',
//   closeBtnClass: 'close',
//   onSubmit: (taskUuid, rating, message) => { ... }
// });

(function(global) {
    const state = {
        currentTaskUuid: null,
        currentRating: 0,
        isSubmitting: false,
    };

    function renderStars(starsDiv, rating, editable = true) {
        starsDiv.innerHTML = '';
        for (let i = 1; i <= 5; i++) {
            const star = document.createElement('span');
            star.className = 'star' + (i <= rating ? ' active' : '');
            star.textContent = '★';
            star.dataset.value = i;
            if (editable) {
                star.style.cursor = 'pointer';
                star.onclick = () => {
                    state.currentRating = i;
                    renderStars(starsDiv, state.currentRating, editable);
                };
            } else {
                star.style.cursor = 'not-allowed';
            }
            starsDiv.appendChild(star);
        }
    }

    function openModal(taskUuid, rating = 0, message = '', config = {}) {
        state.currentTaskUuid = taskUuid;
        state.currentRating = rating;
        state.isSubmitting = false;
        const modal = document.getElementById(config.modalId);
        const starsDiv = document.getElementById(config.starsId);
        const messageInput = document.getElementById(config.messageId);
        const submitBtn = document.getElementById(config.submitBtnId);
        if (!modal || !starsDiv || !messageInput || !submitBtn) return;
        messageInput.value = message || '';
        renderStars(starsDiv, rating, true);
        submitBtn.disabled = false;
        modal.style.display = 'block';
    }

    function closeModal(config) {
        const modal = document.getElementById(config.modalId);
        if (modal) modal.style.display = 'none';
    }

    function bindHandlers(config) {
        const modal = document.getElementById(config.modalId);
        const closeBtn = modal.querySelector('.' + config.closeBtnClass);
        const starsDiv = document.getElementById(config.starsId);
        const messageInput = document.getElementById(config.messageId);
        const submitBtn = document.getElementById(config.submitBtnId);
        if (closeBtn) closeBtn.onclick = () => closeModal(config);
        window.addEventListener('click', function(event) {
            if (event.target === modal) closeModal(config);
        });
        submitBtn.onclick = function() {
            if (state.isSubmitting) return;
            if (!state.currentRating) {
                alert('별점을 선택해주세요!');
                return;
            }
            state.isSubmitting = true;
            submitBtn.disabled = true;
            config.onSubmit && config.onSubmit(state.currentTaskUuid, state.currentRating, messageInput.value, {
                onDone: function() {
                    state.isSubmitting = false;
                    submitBtn.disabled = false;
                    closeModal(config);
                },
                onError: function(msg) {
                    state.isSubmitting = false;
                    submitBtn.disabled = false;
                    alert(msg || '오류가 발생했습니다.');
                }
            });
        };
    }

    global.RatingModal = {
        init: function(config) {
            bindHandlers(config);
        },
        open: openModal,
        close: closeModal,
        renderStars: renderStars,
        state: state
    };
})(window);
