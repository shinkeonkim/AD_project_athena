document.addEventListener('DOMContentLoaded', function() {
    // 요소 선택
    const authTabs = document.querySelectorAll('.auth-tab');
    const authForms = document.querySelectorAll('.auth-form');
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');

    // 유효성 검사 요소
    const registerUsername = document.getElementById('register-username');
    const registerEmail = document.getElementById('register-email');
    const registerPassword = document.getElementById('register-password');
    const registerPasswordConfirm = document.getElementById('register-password-confirm');

    const usernameValidation = document.getElementById('username-validation');
    const emailValidation = document.getElementById('email-validation');
    const passwordValidation = document.getElementById('password-validation');
    const passwordConfirmValidation = document.getElementById('password-confirm-validation');

    // 애니메이션 효과 추가
    function addAnimationEffects() {
        const elementsToAnimate = document.querySelectorAll('.auth-card, .auth-form, .form-group');
        elementsToAnimate.forEach((element, index) => {
            element.style.opacity = '0';
            element.style.transform = 'translateY(20px)';
            element.style.transition = `opacity 0.6s ease ${index * 0.1}s, transform 0.6s ease ${index * 0.1}s`;
        });

        // 초기 애니메이션 실행
        setTimeout(() => {
            elementsToAnimate.forEach(element => {
                element.style.opacity = '1';
                element.style.transform = 'translateY(0)';
            });
        }, 100);
    }

    // 탭 전환 기능
    authTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            // 활성 탭 변경
            authTabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            // 활성 폼 변경
            const tabName = tab.dataset.tab;
            authForms.forEach(form => {
                form.classList.remove('active');
                if (form.id === `${tabName}-form`) {
                    form.classList.add('active');
                }
            });

            // 클릭 효과
            tab.style.transform = 'scale(0.95)';
            setTimeout(() => {
                tab.style.transform = 'scale(1)';
            }, 100);
        });
    });

    // 유효성 검사 함수
    function validateUsername() {
        const username = registerUsername.value.trim();

        if (username.length < 4) {
            registerUsername.classList.add('error');
            registerUsername.classList.remove('valid');
            usernameValidation.textContent = '아이디는 4자 이상이어야 합니다.';
            usernameValidation.classList.add('error');
            usernameValidation.classList.remove('valid');
            return false;
        } else if (!/^[a-zA-Z0-9_]+$/.test(username)) {
            registerUsername.classList.add('error');
            registerUsername.classList.remove('valid');
            usernameValidation.textContent = '아이디는 영문, 숫자, 언더스코어(_)만 포함할 수 있습니다.';
            usernameValidation.classList.add('error');
            usernameValidation.classList.remove('valid');
            return false;
        } else {
            // 서버에 아이디 중복 확인 요청 (실제 구현 시 추가)
            registerUsername.classList.remove('error');
            registerUsername.classList.add('valid');
            usernameValidation.textContent = '사용 가능한 아이디입니다.';
            usernameValidation.classList.remove('error');
            usernameValidation.classList.add('valid');
            return true;
        }
    }

    function validateEmail() {
        const email = registerEmail.value.trim();
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

        if (!emailRegex.test(email)) {
            registerEmail.classList.add('error');
            registerEmail.classList.remove('valid');
            emailValidation.textContent = '유효한 이메일 주소를 입력해주세요.';
            emailValidation.classList.add('error');
            emailValidation.classList.remove('valid');
            return false;
        } else {
            // 서버에 이메일 중복 확인 요청 (실제 구현 시 추가)
            registerEmail.classList.remove('error');
            registerEmail.classList.add('valid');
            emailValidation.textContent = '사용 가능한 이메일입니다.';
            emailValidation.classList.remove('error');
            emailValidation.classList.add('valid');
            return true;
        }
    }

    function validatePassword() {
        const password = registerPassword.value;

        if (password.length < 8) {
            registerPassword.classList.add('error');
            registerPassword.classList.remove('valid');
            passwordValidation.textContent = '비밀번호는 8자 이상이어야 합니다.';
            passwordValidation.classList.add('error');
            passwordValidation.classList.remove('valid');
            return false;
        } else if (!/[A-Z]/.test(password) || !/[a-z]/.test(password) || !/[0-9]/.test(password)) {
            registerPassword.classList.add('error');
            registerPassword.classList.remove('valid');
            passwordValidation.textContent = '비밀번호는 대문자, 소문자, 숫자를 포함해야 합니다.';
            passwordValidation.classList.add('error');
            passwordValidation.classList.remove('valid');
            return false;
        } else {
            registerPassword.classList.remove('error');
            registerPassword.classList.add('valid');
            passwordValidation.textContent = '안전한 비밀번호입니다.';
            passwordValidation.classList.remove('error');
            passwordValidation.classList.add('valid');
            return true;
        }
    }

    function validatePasswordConfirm() {
        const password = registerPassword.value;
        const passwordConfirm = registerPasswordConfirm.value;

        if (password !== passwordConfirm) {
            registerPasswordConfirm.classList.add('error');
            registerPasswordConfirm.classList.remove('valid');
            passwordConfirmValidation.textContent = '비밀번호가 일치하지 않습니다.';
            passwordConfirmValidation.classList.add('error');
            passwordConfirmValidation.classList.remove('valid');
            return false;
        } else if (passwordConfirm.length > 0) {
            registerPasswordConfirm.classList.remove('error');
            registerPasswordConfirm.classList.add('valid');
            passwordConfirmValidation.textContent = '비밀번호가 일치합니다.';
            passwordConfirmValidation.classList.remove('error');
            passwordConfirmValidation.classList.add('valid');
            return true;
        }
        return false;
    }

    // 입력 이벤트 리스너
    registerUsername.addEventListener('blur', validateUsername);
    registerEmail.addEventListener('blur', validateEmail);
    registerPassword.addEventListener('input', validatePassword);
    registerPasswordConfirm.addEventListener('input', validatePasswordConfirm);

    // 폼 제출 이벤트
    loginForm.addEventListener('submit', function(e) {
        // 로딩 효과 추가
        const submitButton = this.querySelector('button[type="submit"]');
        submitButton.classList.add('loading');
        submitButton.textContent = '로그인 중...';

        // 실제 구현 시 서버 응답에 따라 처리
        // 여기서는 기본 동작 유지 (폼 제출)
    });

    registerForm.addEventListener('submit', function(e) {
        e.preventDefault();

        // 모든 유효성 검사 실행
        const isUsernameValid = validateUsername();
        const isEmailValid = validateEmail();
        const isPasswordValid = validatePassword();
        const isPasswordConfirmValid = validatePasswordConfirm();

        // 약관 동의 확인
        const termsChecked = document.getElementById('terms').checked;

        if (isUsernameValid && isEmailValid && isPasswordValid && isPasswordConfirmValid && termsChecked) {
            // 로딩 효과 추가
            const submitButton = this.querySelector('button[type="submit"]');
            submitButton.classList.add('loading');
            submitButton.textContent = '회원가입 중...';

            // 실제 구현 시 서버로 데이터 전송
            // 예시: 폼 데이터 전송
            this.submit();
        } else {
            // 유효성 검사 실패 시 알림
            showNotification('모든 필드를 올바르게 입력해주세요.', 'error');
        }
    });

    // 알림 표시 함수
    function showNotification(message, type = 'info') {
        // 기존 알림 제거
        const existingNotification = document.querySelector('.notification');
        if (existingNotification) {
            existingNotification.remove();
        }

        // 새 알림 생성
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <span>${message}</span>
                <button class="notification-close">×</button>
            </div>
        `;

        document.body.appendChild(notification);

        // 알림 표시 애니메이션
        setTimeout(() => {
            notification.classList.add('show');
        }, 10);

        // 닫기 버튼 이벤트
        const closeBtn = notification.querySelector('.notification-close');
        closeBtn.addEventListener('click', () => {
            notification.classList.remove('show');
            setTimeout(() => {
                notification.remove();
            }, 300);
        });

        // 자동 닫기 (5초 후)
        setTimeout(() => {
            if (document.body.contains(notification)) {
                notification.classList.remove('show');
                setTimeout(() => {
                    if (document.body.contains(notification)) {
                        notification.remove();
                    }
                }, 300);
            }
        }, 5000);
    }

    // 입력 필드 포커스 효과
    const inputFields = document.querySelectorAll('.form-input');
    inputFields.forEach(input => {
        input.addEventListener('focus', function() {
            this.parentElement.classList.add('focused');
        });

        input.addEventListener('blur', function() {
            this.parentElement.classList.remove('focused');
        });
    });

    // 초기화 함수
    function init() {
        addAnimationEffects();
    }

    // 초기화 실행
    init();
});
