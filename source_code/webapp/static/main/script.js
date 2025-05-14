document.addEventListener('DOMContentLoaded', function() {
    // 모바일 메뉴 토글
    const mobileMenuBtn = document.getElementById('mobile-menu-btn');
    const mobileMenu = document.getElementById('mobile-menu');
    const menuIcon = document.getElementById('menu-icon');
    const closeIcon = document.getElementById('close-icon');

    if (mobileMenuBtn) {
        mobileMenuBtn.addEventListener('click', function() {
            mobileMenu.classList.toggle('hidden');
            menuIcon.classList.toggle('hidden');
            closeIcon.classList.toggle('hidden');
        });
    }

    // FAQ 토글 기능
    function toggleFaq(button) {
        const faqItem = button.closest('.faq-item');
        const answer = faqItem.querySelector('.faq-answer');
        const icon = button.querySelector('svg');

        answer.classList.toggle('hidden');

        if (!answer.classList.contains('hidden')) {
            button.classList.add('glow');
            icon.style.transform = 'rotate(180deg)';
        } else {
            button.classList.remove('glow');
            icon.style.transform = 'rotate(0deg)';
        }
    }

    // 전역 함수로 등록
    window.toggleFaq = toggleFaq;

    // 스크롤 애니메이션
    const animateOnScroll = function() {
        const elements = document.querySelectorAll('.glass, .glass-light, .glass-dark');

        elements.forEach(element => {
            const elementPosition = element.getBoundingClientRect().top;
            const windowHeight = window.innerHeight;

            if (elementPosition < windowHeight * 0.8) {
                element.style.opacity = '1';
                element.style.transform = 'translateY(0)';
            }
        });
    };

    // 초기 스타일 설정
    const elementsToAnimate = document.querySelectorAll('.glass, .glass-light, .glass-dark');
    elementsToAnimate.forEach(element => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(20px)';
        element.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    });

    // 스크롤 이벤트 리스너
    window.addEventListener('scroll', animateOnScroll);

    // 초기 애니메이션 실행
    animateOnScroll();

    // 스무스 스크롤 기능 (네비게이션 메뉴에만 적용)
    document.querySelectorAll('nav a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);

            if (targetElement) {
                const headerOffset = 80; // 헤더 높이만큼 오프셋 추가
                const elementPosition = targetElement.getBoundingClientRect().top;
                const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

                window.scrollTo({
                    top: offsetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });
});
