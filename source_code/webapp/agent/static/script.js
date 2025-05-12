document.addEventListener("DOMContentLoaded", () => {
    // 자동완성 기능
    const searchInput = document.getElementById("problem-search")
    const autocompleteResults = document.getElementById("autocomplete-results")
    const submitButton = document.getElementById("submit-btn")
    const codeEditor = document.getElementById("code-editor")
    const languageSelect = document.getElementById("language-select")
    const feedbackContent = document.getElementById("feedback-content")

    let selectedProblemId = null;
    let currentTaskUuid = null;
    let statusCheckInterval = null;

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
            const response = await fetch(`/api/problems/?search=${encodeURIComponent(query)}`);
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return await response.json();
        } catch (error) {
            console.error('Error fetching problems:', error);
            return [];
        }
    }

    // API에서 문제 상세 정보 가져오기
    async function getProblemDetails(problemId) {
        try {
            const response = await fetch(`/api/problems/${problemId}/`);
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return await response.json();
        } catch (error) {
            console.error('Error fetching problem details:', error);
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

        const problems = await searchProblems(inputValue);

        if (problems.length > 0) {
            autocompleteResults.style.display = "block";

            problems.forEach((problem) => {
                const item = document.createElement("div");
                item.className = "autocomplete-item";
                item.textContent = `[${problem.boj_id}] ${problem.title} (${problem.level})`;
                item.dataset.id = problem.id;

                item.addEventListener("click", async () => {
                    searchInput.value = problem.title;
                    autocompleteResults.style.display = "none";
                    await loadProblemDetails(problem.id);
                });

                autocompleteResults.appendChild(item);
            });
        } else {
            autocompleteResults.style.display = "none";
        }
    }, 300);

    searchInput.addEventListener("input", updateAutocomplete);

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

        const problemInfoElement = document.getElementById("problem-info");

        let testCasesHTML = "";
        if (problem.test_cases && problem.test_cases.length > 0) {
            problem.test_cases.forEach((testCase, index) => {
                testCasesHTML += `
                    <h4>예제 입력 ${index + 1}</h4>
                    <pre>${testCase.input}</pre>
                    <h4>예제 출력 ${index + 1}</h4>
                    <pre>${testCase.output}</pre>
                `;
            });
        }

        // 추가 정보 표시
        let extraInfoHTML = "";
        if (problem.extra_information) {
            const extraInfo = problem.extra_information;
            extraInfoHTML = `
                <h4>추가 정보</h4>
                <ul>
                    ${extraInfo.time_limit ? `<li>시간 제한: ${extraInfo.time_limit}</li>` : ''}
                    ${extraInfo.memory_limit ? `<li>메모리 제한: ${extraInfo.memory_limit}</li>` : ''}
                    ${extraInfo.accepted_rate ? `<li>정답 비율: ${extraInfo.accepted_rate}</li>` : ''}
                </ul>
            `;
        }

        problemInfoElement.innerHTML = `
            <h2>문제 정보</h2>
            <div class="problem-content">
                <h3>[${problem.boj_id}] ${problem.title}</h3>
                <p>${problem.description}</p>

                <h4>입력</h4>
                <p>${problem.input_description}</p>

                <h4>출력</h4>
                <p>${problem.output_description}</p>

                ${extraInfoHTML}
                ${testCasesHTML}
            </div>
        `;
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
    codeEditor.value = codeTemplates.cpp

    // 언어 변경 시 코드 템플릿 업데이트
    languageSelect.addEventListener("change", function () {
        codeEditor.value = codeTemplates[this.value]
    })

    // 코드 제출 처리
    submitButton.addEventListener("click", async function() {
        if (!selectedProblemId) {
            alert('문제를 먼저 선택해주세요.');
            return;
        }

        const code = codeEditor.value;
        const language = languageSelect.value;

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
                startStatusChecking();
            } else {
                alert('제출 중 오류가 발생했습니다: ' + data.error);
            }
        } catch (error) {
            alert('제출 중 오류가 발생했습니다.');
            console.error(error);
        }
    });

    // 상태 확인 시작
    function startStatusChecking() {
        if (statusCheckInterval) {
            clearInterval(statusCheckInterval);
        }

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
                    feedbackContent.innerHTML = '<p>제출이 대기 중입니다...</p>';
                    break;
                case 'IN_PROGRESS':
                    feedbackContent.innerHTML = '<p>코드 실행 중입니다...</p>';
                    break;
                case 'COMPLETED':
                    feedbackContent.innerHTML = `
                        <h3>피드백</h3>
                        <div class="feedback-text">${data.feedback}</div>
                    `;
                    clearInterval(statusCheckInterval);
                    break;
                case 'FAILED':
                    feedbackContent.innerHTML = '<p class="error">코드 실행 중 오류가 발생했습니다.</p>';
                    clearInterval(statusCheckInterval);
                    break;
            }
        } catch (error) {
            console.error('상태 확인 중 오류 발생:', error);
            clearInterval(statusCheckInterval);
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
});
