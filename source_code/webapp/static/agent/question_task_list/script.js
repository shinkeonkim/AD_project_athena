document.addEventListener('DOMContentLoaded', function() {
    // 더보기 버튼 클릭 이벤트
    document.querySelectorAll('.expand-btn').forEach(button => {
        button.addEventListener('click', function() {
            const taskId = this.dataset.taskId;
            const details = document.getElementById(`task-${taskId}`);

            if (details.style.display === 'none') {
                details.style.display = 'block';
                this.textContent = '접기';
            } else {
                details.style.display = 'none';
                this.textContent = '더보기';
            }
        });
    });

    // 모달 관련 요소
    const modal = document.getElementById('modal');
    const modalContent = document.getElementById('modal-content');
    const closeBtn = document.querySelector('.close');

    // 모달 닫기
    function closeModal() {
        modal.style.display = 'none';
        modalContent.textContent = '';
    }

    // 모달 닫기 버튼 클릭
    closeBtn.addEventListener('click', closeModal);

    // 모달 외부 클릭시 닫기
    window.addEventListener('click', function(event) {
        if (event.target === modal) {
            closeModal();
        }
    });

    // 전체 코드 보기
    document.querySelectorAll('.view-full-code').forEach(button => {
        button.addEventListener('click', function() {
            const code = this.dataset.code;
            modalContent.textContent = code;
            modal.style.display = 'block';
        });
    });

    // 전체 피드백 보기
    document.querySelectorAll('.view-full-feedback').forEach(button => {
        button.addEventListener('click', function() {
            const feedback = this.dataset.feedback;
            modalContent.textContent = feedback;
            modal.style.display = 'block';
        });
    });

    // 전체 결과 보기
    document.querySelectorAll('.view-full-result').forEach(button => {
        button.addEventListener('click', function() {
            const result = this.dataset.result;
            modalContent.textContent = result;
            modal.style.display = 'block';
        });
    });
});
