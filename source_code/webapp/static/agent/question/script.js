document.addEventListener("DOMContentLoaded", () => {
    // 요소 선택
    const searchInput = document.getElementById("problem-search");
    const autocompleteResults = document.getElementById("autocomplete-results");
    const submitButton = document.getElementById("submit-btn");
    const codeEditor = document.getElementById("code-editor");
    const languageSelect = document.getElementById("language-select");
    const feedbackContent = document.getElementById("feedback-content");
    const problemInfo = document.querySelector('.problem-info');
    const feedbackArea = document.querySelector('.feedback-area');

    // 상태 변수
    let selectedProblemId = null;
    let currentTaskUuid = null;
    let statusCheckInterval = null;
    let lastSearchValue = "";

    // 애니메이션 효과 추가
    function addAnimationEffects() {
        const elementsToAnimate = document.querySelectorAll('.glass, .glass-light, .glass-dark, .problem-content, .feedback-content');
        elementsToAnimate.forEach(element => {
            element.style.opacity = '0';
            element.style.transform = 'translateY(20px)';
            element.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        });

        // 초기 애니메이션 실행
        setTimeout(() => {
            animateOnScroll();
        }, 100);
    }

    // 스크롤 애니메이션
    const animateOnScroll = function() {
        const elements = document.querySelectorAll('.glass, .glass-light, .glass-dark, .problem-content, .feedback-content');

        elements.forEach(element => {
            const elementPosition = element.getBoundingClientRect().top;
            const windowHeight = window.innerHeight;

            if (elementPosition < windowHeight * 0.9) {
                element.style.opacity = '1';
                element.style.transform = 'translateY(0)';
            }
        });
    };

    // 스크롤 이벤트 리스너
    window.addEventListener('scroll', animateOnScroll);

    // 디바운스 함수
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // API에서 문제 검색
    async function searchProblems(query) {
        try {
            // 로딩 효과 추가
            searchInput.classList.add('loading');

            const response = await fetch(`/api/problems/?search=${encodeURIComponent(query)}`);
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            // 로딩 효과 제거
            searchInput.classList.remove('loading');

            return await response.json();
        } catch (error) {
            console.error('Error fetching problems:', error);
            searchInput.classList.remove('loading');
            return [];
        }
    }

    // API에서 문제 상세 정보 가져오기
    async function getProblemDetails(problemId) {
        try {
            // 로딩 효과 추가
            problemInfo.innerHTML = `
                <div class="loading-container">
                    <div class="loading-spinner"></div>
                    <p class="text-gray-300">문제 정보를 불러오는 중...</p>
                </div>
            `;

            const response = await fetch(`/api/problems/${problemId}/`);
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            return await response.json();
        } catch (error) {
            console.error('Error fetching problem details:', error);
            problemInfo.innerHTML = `
                <div class="error-container">
                    <p class="text-red-500">문제 정보를 불러오는 중 오류가 발생했습니다.</p>
                </div>
            `;
            return null;
        }
    }

    // 자동완성 결과 표시
    const updateAutocomplete = debounce(async function() {
        const inputValue = searchInput.value.toLowerCase();
        autocompleteResults.innerHTML = "";

        if (inputValue.length < 1) {
            autocompleteResults.style.display = "none";
            return;
        }

        // 로딩 표시
        autocompleteResults.innerHTML = `
            <div class="autocomplete-loading">
                <div class="loading-spinner-small"></div>
                <span class="text-gray-300">검색 중...</span>
            </div>
        `;
        autocompleteResults.style.display = "block";

        const problems = await searchProblems(inputValue);

        if (problems.length > 0) {
            autocompleteResults.innerHTML = "";

            problems.forEach((problem) => {
                const item = document.createElement("div");
                item.className = "autocomplete-item glass-light";

                // 난이도에 따른 색상 클래스 추가
                let levelClass = '';
                if (problem.level) {
                    const level = parseInt(problem.level);
                    if (level <= 5) levelClass = 'level-easy';
                    else if (level <= 10) levelClass = 'level-medium';
                    else levelClass = 'level-hard';
                }

                item.innerHTML = `
                    <span class="problem-id">${problem.boj_id}</span>
                    <span class="problem-title">${problem.title}</span>
                    <span class="problem-level ${levelClass}">${problem.level || 'N/A'}</span>
                `;
                item.dataset.id = problem.id;

                item.addEventListener("click", async () => {
                    searchInput.value = `[${problem.boj_id}] ${problem.title}`;
                    lastSearchValue = searchInput.value;
                    autocompleteResults.style.display = "none";

                    // 클릭 효과
                    item.classList.add('clicked');
                    setTimeout(() => {
                        item.classList.remove('clicked');
                    }, 200);

                    await loadProblemDetails(problem.id);
                });

                autocompleteResults.appendChild(item);
            });
        } else {
            autocompleteResults.innerHTML = `
                <div class="autocomplete-no-results">
                    <span class="text-gray-300">검색 결과가 없습니다</span>
                </div>
            `;
        }
    }, 300);

    // 입력 이벤트 처리
    searchInput.addEventListener("input", updateAutocomplete);

    // 백스페이스 키 처리
    searchInput.addEventListener("keydown", (e) => {
        if (e.key === "Backspace") {
            // 현재 입력값이 마지막 저장된 값과 같을 때만 (완성된 상태) 한번에 지우기
            if (searchInput.value === lastSearchValue && lastSearchValue !== "") {
                searchInput.value = "";
                lastSearchValue = "";
                autocompleteResults.style.display = "none";
                e.preventDefault();
            }
        }
    });

    // 포커스 이벤트 처리
    searchInput.addEventListener("focus", async () => {
        // 포커스 효과
        searchInput.parentElement.classList.add('focused');

        // 포커스 시 현재 입력값으로 검색 실행
        if (searchInput.value.length > 0) {
            updateAutocomplete();
        } else {
            // 로딩 표시
            autocompleteResults.innerHTML = `
                <div class="autocomplete-loading">
                    <div class="loading-spinner-small"></div>
                    <span class="text-gray-300">문제 목록 불러오는 중...</span>
                </div>
            `;
            autocompleteResults.style.display = "block";

            // 빈 입력값일 경우 전체 목록 조회
            const problems = await searchProblems("");
            if (problems.length > 0) {
                autocompleteResults.innerHTML = "";

                problems.forEach((problem) => {
                    const item = document.createElement("div");
                    item.className = "autocomplete-item glass-light";

                    // 난이도에 따른 색상 클래스 추가
                    let levelClass = '';
                    if (problem.level) {
                        const level = parseInt(problem.level);
                        if (level <= 5) levelClass = 'level-easy';
                        else if (level <= 10) levelClass = 'level-medium';
                        else levelClass = 'level-hard';
                    }

                    item.innerHTML = `
                        <span class="problem-id">${problem.boj_id}</span>
                        <span class="problem-title">${problem.title}</span>
                        <span class="problem-level ${levelClass}">${problem.level || 'N/A'}</span>
                    `;
                    item.dataset.id = problem.id;

                    item.addEventListener("click", async () => {
                        searchInput.value = `[${problem.boj_id}] ${problem.title}`;
                        lastSearchValue = searchInput.value;
                        autocompleteResults.style.display = "none";

                        // 클릭 효과
                        item.classList.add('clicked');
                        setTimeout(() => {
                            item.classList.remove('clicked');
                        }, 200);

                        await loadProblemDetails(problem.id);
                    });

                    autocompleteResults.appendChild(item);
                });
            } else {
                autocompleteResults.innerHTML = `
                    <div class="autocomplete-no-results">
                        <span class="text-gray-300">문제 목록을 불러올 수 없습니다</span>
                    </div>
                `;
            }
        }
    });

    // 포커스 아웃 이벤트 처리
    searchInput.addEventListener("blur", () => {
        searchInput.parentElement.classList.remove('focused');
    });

    // 문서 클릭 시 자동완성 결과 숨기기
    document.addEventListener("click", (e) => {
        if (e.target !== searchInput && !autocompleteResults.contains(e.target)) {
            autocompleteResults.style.display = "none";
        }
    });

    // 문제 상세 정보 로드
    async function loadProblemDetails(problemId) {
        const problem = await getProblemDetails(problemId);
        if (!problem) return;

        selectedProblemId = problemId;
        submitButton.disabled = false;
        submitButton.classList.add('glow');

        const problemInfoElement = document.getElementById("problem-info");

        // 테스트 케이스 HTML 생성
        let testCasesHTML = "";
        if (problem.test_cases && problem.test_cases.length > 0) {
            problem.test_cases.forEach((testCase, index) => {
                testCasesHTML += `
                    <div class="test-case glass-light">
                        <h4 class="text-primary">예제 입력 ${index + 1}</h4>
                        <pre>${testCase.input}</pre>
                        <h4 class="text-primary">예제 출력 ${index + 1}</h4>
                        <pre>${testCase.output}</pre>
                    </div>
                `;
            });
        }

        // 추가 정보 표시
        let extraInfoHTML = "";
        if (problem.extra_information) {
            const extraInfo = problem.extra_information;
            extraInfoHTML = `
                <div class="extra-info glass-light">
                    <h4 class="text-primary">추가 정보</h4>
                    <ul class="text-gray-300">
                        ${extraInfo.time_limit ? `<li><span class="info-label">시간 제한:</span> ${extraInfo.time_limit}</li>` : ''}
                        ${extraInfo.memory_limit ? `<li><span class="info-label">메모리 제한:</span> ${extraInfo.memory_limit}</li>` : ''}
                        ${extraInfo.accepted_rate ? `<li><span class="info-label">정답 비율:</span> ${extraInfo.accepted_rate}</li>` : ''}
                    </ul>
                </div>
            `;
        }

        // 난이도에 따른 색상 클래스 추가
        let levelClass = '';
        if (problem.level) {
            const level = parseInt(problem.level);
            if (level <= 5) levelClass = 'level-easy';
            else if (level <= 10) levelClass = 'level-medium';
            else levelClass = 'level-hard';
        }

        // 문제 정보 HTML 생성
        problemInfoElement.innerHTML = `
            <h2 class="section-title text-primary font-bold">문제 정보</h2>
            <div class="problem-content">
                <div class="problem-header">
                    <h3 class="problem-title text-white">
                        <span class="problem-id">[${problem.boj_id}]</span>
                        ${problem.title}
                    </h3>
                    <span class="problem-level ${levelClass}">${problem.level || 'N/A'}</span>
                </div>

                <div class="problem-description">
                    <p class="text-gray-300">${problem.description}</p>
                </div>

                <div class="problem-section">
                    <h4 class="section-subtitle text-primary">입력</h4>
                    <p class="text-gray-300">${problem.input_description}</p>
                </div>

                <div class="problem-section">
                    <h4 class="section-subtitle text-primary">출력</h4>
                    <p class="text-gray-300">${problem.output_description}</p>
                </div>

                ${extraInfoHTML}

                <div class="test-cases-container">
                    ${testCasesHTML}
                </div>
            </div>
        `;

        // 애니메이션 효과 적용
        animateOnScroll();
    }

    // 언어 선택에 따른 기본 코드 템플릿
    const codeTemplates = {
        cpp: `#include <iostream>
using namespace std;

int main() {
    // 여기에 코드를 작성하세요

    return 0;
}`,
        python: `# 여기에 코드를 작성하세요

def solution():
    # 코드 작성
    pass

if __name__ == "__main__":
    solution()`,
        java: `import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        // 여기에 코드를 작성하세요

    }
}`,
        ruby: `# 여기에 코드를 작성하세요

def solution
  # 코드 작성
end

solution`,
    }

    // 초기 코드 템플릿 설정
    codeEditor.value = codeTemplates.cpp;

    // 언어 변경 시 코드 템플릿 업데이트
    languageSelect.addEventListener("change", function () {
        // 변경 효과
        this.classList.add('changed');
        setTimeout(() => {
            this.classList.remove('changed');
        }, 300);

        codeEditor.value = codeTemplates[this.value];
    });

    // 코드 에디터 포커스 효과
    codeEditor.addEventListener('focus', function() {
        this.parentElement.classList.add('focused');
    });

    codeEditor.addEventListener('blur', function() {
        this.parentElement.classList.remove('focused');
    });

    // 코드 제출 처리
    submitButton.addEventListener("click", async function() {
        if (!selectedProblemId) {
            showNotification('문제를 먼저 선택해주세요.', 'error');
            return;
        }

        const code = codeEditor.value;
        const language = languageSelect.value;

        // 버튼 상태 변경
        this.disabled = true;
        this.classList.add('loading');
        this.textContent = '제출 중...';

        try {
            const response = await fetch('/api/agents/questions/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    problem_id: selectedProblemId,
                    code: code,
                    language: language
                })
            });

            const data = await response.json();
            if (response.ok) {
                currentTaskUuid = data.task_uuid;
                showNotification('코드가 성공적으로 제출되었습니다.', 'success');
                startStatusChecking();
            } else {
                showNotification('제출 중 오류가 발생했습니다: ' + data.error, 'error');
                this.disabled = false;
                this.classList.remove('loading');
                this.textContent = '제출하기';
            }
        } catch (error) {
            showNotification('제출 중 오류가 발생했습니다.', 'error');
            console.error(error);
            this.disabled = false;
            this.classList.remove('loading');
            this.textContent = '제출하기';
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
        notification.className = `notification notification-${type} glass-dark`;
        notification.innerHTML = `
            <div class="notification-content">
                <span class="text-gray-300">${message}</span>
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

    // 상태 확인 시작
    function startStatusChecking() {
        if (statusCheckInterval) {
            clearInterval(statusCheckInterval);
        }

        feedbackContent.innerHTML = `
            <div class="loading-container">
                <div class="loading-spinner"></div>
                <p class="text-gray-300">코드 실행 중입니다...</p>
            </div>
        `;

        statusCheckInterval = setInterval(checkTaskStatus, 1000);
    }

    // 태스크 상태 확인
    async function checkTaskStatus() {
        if (!currentTaskUuid) return;

        try {
            const response = await fetch(`/api/agents/questions/${currentTaskUuid}/status/`);
            const data = await response.json();

            switch (data.status) {
                case 'PENDING':
                    feedbackContent.innerHTML = `
                        <div class="loading-container">
                            <div class="loading-spinner"></div>
                            <p class="text-gray-300">제출이 대기 중입니다...</p>
                        </div>
                    `;
                    break;
                case 'IN_PROGRESS':
                    feedbackContent.innerHTML = `
                        <div class="loading-container">
                            <div class="loading-spinner"></div>
                            <p class="text-gray-300">코드 실행 중입니다...</p>
                        </div>
                    `;
                    break;
                case 'COMPLETED':
                    feedbackContent.innerHTML = `
                        <div class="feedback-result">
                            <div class="feedback-text text-gray-300">${data.feedback}</div>
                        </div>
                    `;
                    clearInterval(statusCheckInterval);
                    submitButton.disabled = false;
                    submitButton.classList.remove('loading');
                    submitButton.textContent = '제출하기';

                    // 애니메이션 효과 적용
                    animateOnScroll();
                    break;
                case 'FAILED':
                    feedbackContent.innerHTML = `
                        <div class="error-container">
                            <h3 class="error-title text-red-500 font-bold">오류 발생</h3>
                            <p class="error-text text-gray-300">코드 실행 중 오류가 발생했습니다.</p>
                        </div>
                    `;
                    clearInterval(statusCheckInterval);
                    submitButton.disabled = false;
                    submitButton.classList.remove('loading');
                    submitButton.textContent = '제출하기';
                    break;
            }
        } catch (error) {
            console.error('상태 확인 중 오류 발생:', error);
            feedbackContent.innerHTML = `
                <div class="error-container">
                    <h3 class="error-title text-red-500 font-bold">오류 발생</h3>
                    <p class="error-text text-gray-300">상태 확인 중 오류가 발생했습니다.</p>
                </div>
            `;
            clearInterval(statusCheckInterval);
            submitButton.disabled = false;
            submitButton.classList.remove('loading');
            submitButton.textContent = '제출하기';
        }
    }

    // CSRF 토큰 가져오기
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

    // 창 크기 변경 시 레이아웃 조정
    window.addEventListener('resize', () => {
        if (window.innerWidth <= 1024) {
            problemInfo.style.cssText = 'height: auto; min-height: 200px;';
            feedbackArea.style.cssText = 'height: auto; min-height: 200px;';
        }
    });

    // 초기화 함수
    function init() {
        addAnimationEffects();
    }

    // 초기화 실행
    init();
});
